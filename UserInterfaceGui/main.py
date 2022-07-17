import inspect
import threading
from os import listdir
from os.path import isfile, join
from tkinter import *
from tkinter import ttk
from Framework.cDaq import *
import serial.tools.list_ports
from PIL import ImageTk, Image
from pandastable import Table
from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF, renderPM

from Framework.HIT_Putty_Interface import HIT_Interface, reset_menu, CR, LF, encode_style
from Tests.test_serialinterface import *
from Tests.test_sampleTest import *
import Tests


def find_path(test_case) -> str:
    """
    This is a function that helps find the path to a Test file
    :param test_case: The test case that is to be chosen
    :return: The relative path
    """
    path = Path(test_case)
    absPath = str(path.parent.absolute())
    dirPath = '\\'.join(absPath.split('\\')[0:-1])
    relPath = f'{dirPath}\\Tests\\{test_case}'
    return relPath


class App(Tk):
    """
    This is an App for HIT testing and controlling the PSU and DAQ
    """

    def __init__(self):
        """
        This is a method that stores important variables and functions that are used in the app
        """
        super().__init__()

        # self.resizable(False, False)
        # self.attributes('-full-screen', True)
        self.threads = []
        # Variables for Configuring HIT
        self.inter_byte_timeout = None
        self.timeout = "None"
        self.bytesize = "None"
        self.stopbits = "None"
        self.parity = "None"
        self.baudrate = "None"
        self.hit = None
        self.comPort2 = StringVar()
        # Variable for Configuring PSU
        self.gui_psu = None
        self.comPort1 = StringVar()
        # Variable for Table
        self.pt = None
        self.csvFile = StringVar(self)
        # Variable for Setting Basic Voltage
        self.set_voltage = StringVar()
        # Variable for Setting Basic Current
        self.set_current = StringVar()
        # Variable for Setting Basic Output State
        self.output_state = IntVar()
        # Variable for Selecting Basic Channel
        self.psu_channel = StringVar(self)
        # Variable for Getting Basic Voltage
        self.get_voltage = StringVar()
        # Variable for Getting Basic Current
        self.get_current = StringVar()
        # Variable for Getting Basic Output State
        self.get_output_state = StringVar()
        # Variable for Getting Basic Channel
        self.psu_get_channel = StringVar(self)
        # Variable for Setting Basic Output of All Channels
        self.output_all = IntVar()
        # Variable for Setting Advance Voltage Method
        self.psu_adv_set_volt = StringVar()
        # Variable for Setting Advance Voltage
        self.set_adv_volts = StringVar()
        # Variable for Setting Advance Channel
        self.adv_psu_channel = StringVar(self)
        # Variable for Volts inc/dec [Advanced Section]
        self.psu_volts_inc_dec = IntVar()
        # Variable for Volts verify [Advanced Section]
        self.adv_verify_volt = IntVar()
        # Variable for Volts interval [Advanced Section]
        self.adv_volts_interval = StringVar()
        # Variable for Getting Volts [Advanced Section]
        self.adv_get_voltage = StringVar()
        # Variable for Getting Volts Readback [Advanced Section]
        self.adv_get_volt_readback = StringVar()
        # Variable for Getting Volts Delta [Advanced Section]
        self.adv_get_volt_delta = StringVar()
        # Variable for Getting Volts Channel [Advanced Section]
        self.psu_adv_get_volt_channel = StringVar(self)
        # Variable for Setting Current [Advanced Section]
        self.psu_adv_set_curr = StringVar()
        # Variable for Setting Current [Advanced Section]
        self.set_adv_curr = StringVar()
        # Variable for Setting Current Channel [Advanced Section]
        self.adv_psu_curr_channel = StringVar(self)
        # Variable for Current inc/dec [Advanced Section]
        self.psu_curr_inc_dec = IntVar()
        # Variable for Getting Current [Advanced Section]
        self.adv_get_current = StringVar()
        # Variable for Getting Current Readback [Advanced Section]
        self.adv_get_curr_readback = StringVar()
        # Variable for Getting Current Delta [Advanced Section]
        self.adv_get_curr_delta = StringVar()
        # Variable for Getting Current Channel [Advanced Section]
        self.psu_adv_get_curr_channel = StringVar(self)
        # Variable for Setting Lock Status [Diagnostic Section]
        self.lock_status = StringVar()
        # Variable for Getting OP Status [Diagnostic Section]
        self.get_op_status = StringVar()
        # Variable for Setting Ratio [Diagnostic Section]
        self.set_ratio = StringVar()
        # Variable for Getting Ratio [Diagnostic Section]
        self.get_ratio = StringVar()
        # Variable for Getting Operating Mode [Diagnostic Section]
        self.psu_operating_mode = IntVar()
        """
        ******************************************************************************************************
        App Methods 
        ******************************************************************************************************
        """
        # Function for the menu
        menuBar = Menu(self)
        self.config(menu=menuBar)
        file = Menu(menuBar, tearoff=0)
        menuBar.add_cascade(label='Settings', menu=file)
        file.add_command(label='About')
        file.add_separator()
        file.add_command(label='Connect to HIT/PSU', command=self.configuration)
        file.add_command(label='Connect to PSU(only)', command=self.connect_psu)
        file.add_command(label='Exit', compound=LEFT, command=self.funcExit)
        # Function for configuration settings of app
        self.title("Rockwell Automation HIT GUI")
        # self.call('source', r'C:\Users\RMartin10\PycharmProjects\Rasheedattempt\UserInterfaceGui\Forest-ttk-theme'
        #                     r'-master\forest-dark.tcl')
        # ttk.Style(self).theme_use("forest-dark")
        # self.option_add("*tearOff", False)
        # Make the app responsive
        # self.columnconfigure(index=0, weight=1)
        # self.columnconfigure(index=1, weight=1)
        # self.columnconfigure(index=2, weight=1)
        # self.rowconfigure(index=0, weight=1)
        # self.rowconfigure(index=1, weight=1)
        # self.rowconfigure(index=2, weight=1)
        # Center the window, and set minsize
        # self.update()
        # self.minsize(self.winfo_width(), self.winfo_height())
        # x_coordinate = int((self.winfo_screenwidth() / 2) - (self.winfo_width() / 2))
        # y_coordinate = int((self.winfo_screenheight() / 2) - (self.winfo_height() / 2))
        # self.geometry("+{}+{}".format(x_coordinate, y_coordinate))
        self.geometry("+0+0")
        # Function for creation of tabs
        tabs = ttk.Notebook(self)
        tabs.pack(fill=BOTH, expand=True)
        self.tab1 = Frame(tabs)

        # tabs.add(tab2, text='Second Tab', image=icon, compound=LEFT)

        tabs.add(self.tab1, text='HIT')

        """
        ******************************************************************************************************
        HIT Tab
        ******************************************************************************************************
        """
        # Function for Data Table Section
        tableFrame = LabelFrame(self.tab1, text='CSVs')
        tableFrame.grid(row=0, column=0, rowspan=3, padx=(20, 10), pady=(20, 10), sticky="nsew")
        self.pt = Table(tableFrame, editable=False, showtoolbar=True, showstatusbar=True, rows=25, cols=20)
        # pt.importCSV(r'C:\Users\RMartin10\PycharmProjects\Rasheedattempt\CSVs\adc.csv')
        self.pt.setTheme("dark")
        self.pt.setRowColors(clr='red')
        self.pt.show()
        # Function for Reading of Data section
        readingData = LabelFrame(self.tab1, text='Reading of Data')
        readingData.grid(row=0, column=4, padx=(20, 20), pady=(20, 10), sticky="nsew")
        Label(readingData, text="Select a CSV to Read").grid(row=0, column=1, padx=(20, 20),
                                                             pady=(20, 10), sticky="nsew")

        # Combo Box
        path = Path(' ')
        absPath = str(path.parent.absolute())
        dirPath = '\\'.join(absPath.split('\\')[0:-1])
        relPath = f'{dirPath}\\CSVs'
        csv_files = [f for f in listdir(relPath) if isfile(join(relPath, f))]
        comboBox1 = ttk.Combobox(readingData, textvariable=self.csvFile, values=csv_files,
                                 state='readonly')
        comboBox1.grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        # Button
        button1 = Button(readingData, text="Read Data", command=lambda: self.reading_data())
        button1.grid(row=2, column=1, padx=10, pady=5, sticky="nsew", columnspan=2)
        # Function for Interface Section
        # Frame
        interface_frame = LabelFrame(self.tab1, text='Interface')
        interface_frame.grid(row=0, column=3, padx=(20, 10), pady=(20, 10), sticky="nsew")

        # Listbox
        self.interface_listBox = Listbox(interface_frame, width=40, height=5, selectmode=MULTIPLE, justify=CENTER)
        [self.interface_listBox.insert(x, y[0]) for x, y
         in enumerate(inspect.getmembers(HIT_Interface, predicate=inspect.isfunction))
         if ('_' not in y[0][0] and 'readBytes' not in y[0])]

        self.interface_listBox.grid(row=0, column=1, pady=20, padx=20, sticky="nsew")

        # self.interface_listBox.bind("<<ListboxSelect>>", self.interface_listBox_selection)
        self.interface_checkbutton = BooleanVar()
        Checkbutton(interface_frame, variable=self.interface_checkbutton, text="Select all",
                    command=self.select_all).grid(row=1, column=1)
        self.interface_tracker_label = Label(interface_frame, text="No interface is running right now",
                                             foreground='red')
        self.interface_tracker_label.grid(row=2, column=1)
        # Buttons
        interface_button1 = Button(interface_frame,
                                   text='Run Interface(s)',
                                   command=lambda: self.create_thread(self.run_interface),
                                   width=20)
        interface_button1.grid(row=3, column=1, columnspan=1, pady=10, padx=20, sticky="nsew")
        interface_scrollbar = Scrollbar(interface_frame, orient=VERTICAL)
        interface_scrollbar.grid(row=0, column=2, sticky=NS)
        self.interface_listBox.config(yscrollcommand=interface_scrollbar.set)
        interface_scrollbar.config(command=self.interface_listBox.yview)
        # Function for Logo Section
        image1 = Image.open('rockwell_logo.jpg')
        image1.resize((40, 40))
        logo = ImageTk.PhotoImage(image1)
        lbl_image = Label(self.tab1, image=logo)
        lbl_image.image = logo
        lbl_image.grid(row=1, column=3, columnspan=2)
        """
        ******************************************************************************************************
        HIT Testing
        ******************************************************************************************************
        """
        self.tab2 = Frame(tabs)
        tabs.add(self.tab2, text="HIT Testing")
        # Function for Test Section
        testFrame = LabelFrame(self.tab2, text="Tests")
        testFrame.grid(row=1, column=3, padx=(20, 10), pady=(20, 10), sticky="nsew")
        # Listbox
        self.testBox = Listbox(testFrame, width=40, height=5, selectmode=MULTIPLE, justify=CENTER)

        self.name = [x for x in dir(Tests) if "__" not in x]
        self.classes = [[i for i in dir(getattr(Tests, x)) if "Test" in i] for x in self.name]

        display = []
        self.tests = []
        for x, y in zip(self.name, sum(self.classes, [])):
            display.append(inspect.getmembers(getattr(getattr(Tests, x), y), predicate=inspect.isfunction))
        print(self.tests)
        for x, y in enumerate(sum(display, [])):
            self.testBox.insert(x, y[0])

        self.testBox.grid(row=0, column=1, pady=20, padx=20, sticky="nsew")
        self.testing_checkbutton = BooleanVar()
        Checkbutton(testFrame, variable=self.testing_checkbutton, text="Select all",
                    command=self.test_select_all).grid(row=1, column=1)
        # Label
        self.test_tracker_label = Label(testFrame, text="No test is running right now", foreground='red')
        self.test_tracker_label.grid(row=2, column=1)
        # Button
        Button(testFrame, text='Run Test(s)',
               command=lambda: self.create_thread(self.test_interface),
               width=10).grid(row=3, column=1, pady=10, padx=20, sticky="nsew")
        # Scrollbar
        test_scroll_bar = Scrollbar(testFrame, orient=VERTICAL)
        test_scroll_bar.grid(row=0, column=2, sticky=NS)

        self.testBox.config(yscrollcommand=test_scroll_bar.set)
        test_scroll_bar.config(command=self.testBox.yview)
        self.path = Path('out.txt')
        self.absPath = str(self.path.parent.absolute())
        self.dirPath = '\\'.join(self.absPath.split('\\')[0:-1])

        # Test Results
        user_frame1 = LabelFrame(self.tab2, text='Test Results')
        user_response_frame1 = Frame(self.tab2)
        user_response_frame1.grid(row=0, column=1)
        m = Message(user_frame1)
        user_scroll_bar1 = Scrollbar(user_frame1, orient=VERTICAL)
        user_scroll_bar1.grid(row=0, column=1, sticky=NS, rowspan=2)
        self.txt1 = Text(user_frame1, bg='white', relief=SUNKEN,
                         borderwidth=1, font=m.cget("font"), width=120, height=30,
                         state="normal", wrap=WORD, yscrollcommand=user_scroll_bar1.set)
        self.txt1.grid(row=0, column=0, rowspan=2)
        Button(self.tab2, text="Clear", bg='red', command=self.reset_test_interface).grid(row=10, column=0, rowspan=10)
        user_scroll_bar1.config(command=self.txt1.yview)
        m.destroy()
        user_frame1.grid(row=0, column=0, padx=20, pady=20, rowspan=10)
        self.txt1.config(state='disabled')
        # Function for Logo Section 2
        logo = ImageTk.PhotoImage(image1)
        lbl_image2 = Label(self.tab2, image=logo)
        lbl_image2.image = logo
        lbl_image2.grid(row=2, column=1, rowspan=10, columnspan=3)
        """
        ******************************************************************************************************
        HIT User Interaction
        ******************************************************************************************************
        """
        self.tab3 = Frame(tabs)
        tabs.add(self.tab3, text='HIT User Interaction')
        # User Interface
        user_frame = LabelFrame(self.tab3, text='User Interface')
        user_response_frame = Frame(self.tab3)
        user_response_frame.grid(row=0, column=1)
        user_response_frame2 = Frame(self.tab3)
        user_response_frame2.grid(row=11, column=0)
        m = Message(user_frame)
        user_scroll_bar = Scrollbar(user_frame, orient=VERTICAL)
        user_scroll_bar.grid(row=0, column=1, sticky=NS, rowspan=2)
        self.txt = Text(user_frame, bg='white', relief=SUNKEN,
                        borderwidth=1, font=m.cget("font"), width=90, height=30,
                        state="normal", wrap=WORD, yscrollcommand=user_scroll_bar.set)
        self.txt.grid(row=0, column=0, rowspan=2)
        user_scroll_bar.config(command=self.txt.yview)
        m.destroy()
        user_frame.grid(row=0, column=0, padx=20, pady=20, rowspan=10)
        self.txt.config(state='disabled')
        Button(user_response_frame, text="Run", width=10, command=lambda: self.create_thread(self.user_interface)). \
            grid(row=2, column=1, padx=10, pady=5, sticky=EW)
        label = Label(user_response_frame, text="Enter your response", foreground='Black')
        label.grid(row=0, column=1, padx=10, pady=10, sticky=NSEW)

        self.user_input = StringVar()
        entry = Entry(user_response_frame, textvariable=self.user_input, width=30, relief=SUNKEN)
        entry.grid(row=0, column=2, padx=10, pady=10, sticky=EW)
        entry.insert(0, "")
        entry.bind("<Return>", self.submission)
        self.user_interface_label = Label(user_response_frame, text="This has not been ran", foreground='red')
        self.user_interface_label.grid(row=1, column=2)
        self.button_pressed = BooleanVar()
        self.button = Button(user_response_frame, text="Enter", command=lambda: self.submission())
        self.button.grid(row=2, column=2, padx=10, pady=5, sticky=EW)
        Button(user_response_frame2, text="Reset", bg='red', fg='white', command=lambda: self.reset_user_interface()). \
            grid(row=0, column=0, padx=10, pady=5, sticky=EW)
        Button(user_response_frame2, text="Clear", command=lambda: self.clear()). \
            grid(row=0, column=1, padx=10, pady=5, sticky=EW)
        Button(user_response_frame2, text="Stop", command=lambda: self.stop_user_interface()). \
            grid(row=0, column=2, padx=10, pady=5, sticky=EW)
        self.method_ran = BooleanVar()
        self.method_ran.set(False)
        # Function for Logo Section 3
        lbl_image3 = Label(self.tab3, image=logo)
        lbl_image3.image = logo
        lbl_image3.grid(row=1, column=1, rowspan=10)
        """
        ******************************************************************************************************
        PSU Control
        ******************************************************************************************************
        """
        self.tab4 = Frame(tabs)
        tabs.add(self.tab4, text='PSU Controls')
        # Function for PSU Basic Control Section
        # SET Functions
        # Label Frame
        psu_frame = LabelFrame(self.tab4, text="Basic PSU Control")
        psu_frame.grid(row=0, column=2, rowspan=10, padx=(20, 10), pady=(20, 10), sticky="nsew")
        # Voltage
        Label(psu_frame, text="Set Voltage").grid(row=0, column=0, padx=10, pady=5,
                                                  sticky="nsew")

        Spinbox(psu_frame, from_=0, to=24, textvariable=self.set_voltage, format="%.2f", increment=0.01).grid(
            row=0, column=1, padx=10, pady=5, sticky="nsew")
        # Current
        psu_setcurrent_label = Label(psu_frame, text="Set Current")
        psu_setcurrent_label.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        Spinbox(psu_frame, from_=0.0, to=2.0, textvariable=self.set_current,
                format="%.2f", increment=0.01).grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        # Output State
        Label(psu_frame, text="Set Output State").grid(row=2, column=0, padx=10, pady=5,
                                                       sticky="nsew")

        Checkbutton(psu_frame, text='Turn On', variable=self.output_state).grid(row=2, column=1, pady=5)
        # PSU Channel
        Label(psu_frame, text="Set Channel").grid(row=3, column=0, padx=10, pady=5,
                                                  sticky="nsew")

        options_list = ['Channel1', 'Channel2']
        self.psu_channel.set("Select an Option")
        OptionMenu(psu_frame, self.psu_channel, *options_list).grid(row=3, column=1, pady=5, padx=10,
                                                                    sticky="nsew")
        # Button
        Button(psu_frame, text="Set", command=self.psu_voltage_change,
               width=10).grid(row=4, column=1, pady=5, padx=10, sticky="nsew")

        # GET Functions
        # Voltage
        Label(psu_frame, text="Get Voltage").grid(row=5, column=0, padx=10, pady=5,
                                                  sticky="nsew")

        Entry(psu_frame, textvariable=self.get_voltage, state='readonly'). \
            grid(row=5, column=1, padx=10, pady=5, sticky="nsew")
        # Current
        Label(psu_frame, text="Get Current").grid(row=6, column=0, padx=10, pady=5,
                                                  sticky="nsew")

        Entry(psu_frame, textvariable=self.get_current, state='readonly').grid(row=6, column=1, padx=10, pady=5,
                                                                               sticky="nsew")
        # Output State
        Label(psu_frame, text="Get Output State").grid(row=7, column=0, padx=10, pady=5,
                                                       sticky="nsew")

        Entry(psu_frame, textvariable=self.get_output_state, state='readonly').grid(row=7, column=1, padx=10,
                                                                                    pady=5, sticky="nsew")
        # PSU Channel
        Label(psu_frame, text="Get Channel").grid(row=8, column=0, padx=10, pady=5,
                                                  sticky="nsew")

        options_list = ['Channel1', 'Channel2']
        self.psu_get_channel.set("Select an Option")
        OptionMenu(psu_frame, self.psu_get_channel, *options_list).grid(row=8, column=1, pady=5, padx=10, sticky="nsew")
        # Button
        Button(psu_frame, text="Get", command=self.psu_get_info,
               width=10).grid(row=9, column=1, pady=5, padx=10, sticky="nsew")
        # Set Output All
        Label(psu_frame, text="Set Output All").grid(row=10, column=0, padx=10, pady=5,
                                                     sticky="nsew")

        Checkbutton(psu_frame, text="On/Off", variable=self.output_all).grid(row=10, column=1, pady=5)
        Button(psu_frame, text="Set", command=self.set_output_all,
               width=10).grid(row=11, column=1, pady=5, padx=10, sticky="nsew")
        Label(psu_frame, text="Device Reset").grid(row=12, column=0, padx=10, pady=5,
                                                   sticky="nsew")
        Button(psu_frame, text="Hard Reset", command=self.device_settings_reset,
               width=10, bg='red').grid(row=12, column=1, pady=5, padx=10, sticky="nsew")
        # Function for PSU Advance Voltage Control Section
        # SET Functions
        # Label Frame
        psu_adv_frame = LabelFrame(self.tab4, text="Advanced PSU Voltage Control")
        psu_adv_frame.grid(row=0, column=1, padx=(20, 10), pady=(20, 10), sticky="nsew")
        # Voltage
        Label(psu_adv_frame, text="Set Voltage").grid(row=5, column=0, padx=10, pady=5,
                                                      sticky="nsew")
        # Combo Box
        psu_adv_set_volt_funcs = ['set_voltage_trip', 'set_voltage_delta', 'set_voltage_and_wait']
        ttk.Combobox(psu_adv_frame, textvariable=self.psu_adv_set_volt, values=psu_adv_set_volt_funcs,
                     state='readonly').grid(row=5, column=1, padx=10, pady=5, sticky="nsew")

        # Value
        Label(psu_adv_frame, text="Set Value").grid(row=6, column=0, padx=10, pady=5,
                                                    sticky="nsew")
        ttk.Spinbox(psu_adv_frame, from_=0.0, to=24.0, textvariable=self.set_adv_volts,
                    format="%.2f", increment=0.01).grid(row=6, column=1, padx=10, pady=5, sticky="nsew")
        # PSU Channel
        Label(psu_adv_frame, text="Set Channel").grid(row=7, column=0, padx=10, pady=5,
                                                      sticky="nsew")
        options_list = ['Channel1', 'Channel2']
        self.adv_psu_channel.set("Select an Option")
        OptionMenu(psu_adv_frame, self.adv_psu_channel, *options_list). \
            grid(row=7, column=1, pady=5, padx=10, sticky="nsew")
        # Radio Buttons for inc / dec
        Label(psu_adv_frame, text="For set_voltage_delta ONLY", foreground='red').grid(row=8, column=0,
                                                                                       padx=10,
                                                                                       pady=5, sticky="nsew")
        Radiobutton(psu_adv_frame, text='Decrement Voltage', value='0', variable=self.psu_volts_inc_dec).grid(
            row=8, column=1)
        Radiobutton(psu_adv_frame, text='Increment Voltage', value='1', variable=self.psu_volts_inc_dec).grid(
            row=9, column=1)
        Checkbutton(psu_adv_frame, text='Verify', variable=self.adv_verify_volt).grid(row=10, column=1, pady=5)

        # Time Interval Value
        Label(psu_adv_frame, text="For set_voltage_and_wait ONLY", foreground='red'). \
            grid(row=11, column=0, padx=10, pady=5, sticky="nsew")
        Spinbox(psu_adv_frame, from_=0, to=5, textvariable=self.adv_volts_interval) \
            .grid(row=11, column=1, padx=10, pady=5, sticky="nsew")
        # Button
        Button(psu_adv_frame, text="Set",
               width=10, command=self.adv_set_volt).grid(row=12, column=1, pady=5,
                                                         padx=10, sticky="nsew")

        # GET Functions
        # Voltage Trip
        Label(psu_adv_frame, text="Get Voltage Trip").grid(row=5, column=2, padx=10, pady=5,
                                                           sticky="nsew")
        Entry(psu_adv_frame, textvariable=self.adv_get_voltage, state='readonly'). \
            grid(row=5, column=3, padx=10, pady=5, sticky="nsew")
        # Voltage Readback
        Label(psu_adv_frame, text="Get Voltage Readback").grid(row=6, column=2, padx=10, pady=5,
                                                               sticky="nsew")
        Entry(psu_adv_frame, textvariable=self.adv_get_volt_readback, state='readonly'). \
            grid(row=6, column=3, padx=10, pady=5, sticky="nsew")
        # Voltage Delta
        Label(psu_adv_frame, text="Get Voltage Delta").grid(row=7, column=2, padx=10, pady=5,
                                                            sticky="nsew")
        Entry(psu_adv_frame, textvariable=self.adv_get_volt_delta, state='readonly'). \
            grid(row=7, column=3, padx=10, pady=5, sticky="nsew")
        # PSU Channel
        Label(psu_adv_frame, text="Get Channel").grid(row=8, column=2, padx=10, pady=5,
                                                      sticky="nsew")
        options_list = ['Channel1', 'Channel2']
        self.psu_adv_get_volt_channel.set("Select an Option")
        OptionMenu(psu_adv_frame, self.psu_adv_get_volt_channel, *options_list). \
            grid(row=8, column=3, pady=5, padx=10, sticky="nsew")
        # Button
        Button(psu_adv_frame, text="Get", command=self.psu_adv_volt_get_info,
               width=10).grid(row=12, column=3, pady=5, padx=10, sticky="nsew")
        # Function for PSU Advance Current Control Section
        # SET Functions
        # Label Frame
        psu_adv_cur_frame = LabelFrame(self.tab4, text="Advanced PSU Current Control")
        psu_adv_cur_frame.grid(row=1, column=1, padx=(20, 10), pady=(20, 10), sticky="nsew")
        # Voltage
        Label(psu_adv_cur_frame, text="Set Current").grid(row=5, column=0, padx=10, pady=5,
                                                          sticky="nsew")
        # Combo Box
        psu_adv_set_curr_funcs = ['set_current_trip', 'set_current_delta', 'set_current_and_wait']
        ttk.Combobox(psu_adv_cur_frame, textvariable=self.psu_adv_set_curr, values=psu_adv_set_curr_funcs,
                     state='readonly').grid(row=5, column=1, padx=10, pady=5, sticky="nsew")
        # Value
        Label(psu_adv_cur_frame, text="Set Value").grid(row=6, column=0, padx=10, pady=5,
                                                        sticky="nsew")
        Spinbox(psu_adv_cur_frame, from_=0.0, to=24.0, textvariable=self.set_adv_curr,
                format="%.2f", increment=0.01).grid(row=6, column=1, padx=10, pady=5, sticky="nsew")
        # PSU Channel
        Label(psu_adv_cur_frame, text="Set Channel").grid(row=7, column=0, padx=10, pady=5,
                                                          sticky="nsew")
        options_list = ['Channel1', 'Channel2']
        self.adv_psu_curr_channel.set("Select an Option")
        OptionMenu(psu_adv_cur_frame, self.adv_psu_curr_channel, *options_list). \
            grid(row=7, column=1, pady=5, padx=10, sticky="nsew")
        # Radio Buttons for inc / dec
        Label(psu_adv_cur_frame, text="For set_current_delta ONLY", foreground='red').grid(row=8, column=0,
                                                                                           padx=10,
                                                                                           pady=5, sticky="nsew")
        Radiobutton(psu_adv_cur_frame, text='Decrement Current', value='0', variable=self.psu_curr_inc_dec).grid(
            row=8, column=1)
        Radiobutton(psu_adv_cur_frame, text='Increment Current', value='1', variable=self.psu_curr_inc_dec).grid(
            row=9, column=1)
        # Button
        Button(psu_adv_cur_frame, text="Set",
               width=10, command=self.adv_set_curr).grid(row=9, column=0, pady=5,
                                                         padx=10, sticky="nsew")
        # GET Functions
        # Current Trip
        Label(psu_adv_cur_frame, text="Get Current Trip").grid(row=5, column=2, padx=10, pady=5,
                                                               sticky="nsew")
        Entry(psu_adv_cur_frame, textvariable=self.adv_get_current, state='readonly'). \
            grid(row=5, column=3, padx=10, pady=5, sticky="nsew")
        # Current Readback
        Label(psu_adv_cur_frame, text="Get Current Readback").grid(row=6, column=2, padx=10,
                                                                   pady=5,
                                                                   sticky="nsew")
        Entry(psu_adv_cur_frame, textvariable=self.adv_get_curr_readback, state='readonly'). \
            grid(row=6, column=3, padx=10, pady=5, sticky="nsew")
        # Current Delta
        Label(psu_adv_cur_frame, text="Get Current Delta").grid(row=7, column=2, padx=10,
                                                                pady=5,
                                                                sticky="nsew")
        Entry(psu_adv_cur_frame, textvariable=self.adv_get_curr_delta, state='readonly'). \
            grid(row=7, column=3, padx=10, pady=5, sticky="nsew")
        # PSU Channel
        Label(psu_adv_cur_frame, text="Get Channel").grid(row=8, column=2, padx=10, pady=5,
                                                          sticky="nsew")
        options_list = ['Channel1', 'Channel2']
        self.psu_adv_get_curr_channel.set("Select an Option")
        OptionMenu(psu_adv_cur_frame, self.psu_adv_get_curr_channel, *options_list). \
            grid(row=8, column=3, pady=5, padx=10, sticky="nsew")
        # Button
        Button(psu_adv_cur_frame, text="Get", command=self.psu_adv_curr_get_info,
               width=10).grid(row=9, column=3, pady=5, padx=10, sticky="nsew")
        # Function for Logo Section 4
        lbl_image4 = Label(self.tab4, image=logo)
        lbl_image4.image = logo
        lbl_image4.grid(row=1, column=3, rowspan=3, columnspan=3)

        """
        ******************************************************************************************************
        PSU Diagnostics
        ******************************************************************************************************
        """
        self.tab5 = Frame(tabs)
        tabs.add(self.tab5, text="PSU Diagnostics")
        # Function for PSU Interface Locking
        psu_diag_frame = LabelFrame(self.tab5, text="Interface Lock")
        psu_diag_frame.grid(row=0, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")

        Label(psu_diag_frame, text="Set Interface Lock"). \
            grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        Button(psu_diag_frame, text="Set", command=lambda: self.set_interface_lock(),
               width=10).grid(row=0, column=1, pady=5, padx=10, sticky="nsew")
        Label(psu_diag_frame, text="Get Interface Lock"). \
            grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        Entry(psu_diag_frame, textvariable=self.lock_status, state='readonly'). \
            grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        Button(psu_diag_frame, text="Get", command=lambda: self.get_interface_lock(),
               width=10).grid(row=2, column=1, pady=5, padx=10, sticky="nsew")
        Label(psu_diag_frame, text="Release Lock"). \
            grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        Button(psu_diag_frame, text="Release", command=lambda: self.release_lock(),
               width=10).grid(row=3, column=1, pady=5, padx=10, sticky="nsew")
        # Function for Resetting PSU
        psu_reset_frame = LabelFrame(self.tab5, text="Reset Settings")
        psu_reset_frame.grid(row=2, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")
        Label(psu_reset_frame, text="Reset Trip Condition"). \
            grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        Button(psu_reset_frame, text="Reset", command=lambda: self.reset_trip_condition(),
               width=10, bg='red').grid(row=0, column=1, pady=5, padx=10, sticky="nsew")
        Label(psu_reset_frame, text="Release Limit Lock"). \
            grid(row=2, column=0, padx=10, pady=5, sticky="nsew")
        Button(psu_reset_frame, text="Soft Reset", command=lambda: self.release_limit_lock(),
               width=10, bg='red').grid(row=2, column=1, pady=5, padx=10, sticky="nsew")
        # Function for Modes of PSU
        psu_mode_frame = LabelFrame(self.tab5, text="Mode")
        psu_mode_frame.grid(row=0, column=2, padx=(20, 10), pady=(20, 10), sticky="nsew")
        Label(psu_mode_frame, text="Set To Local"). \
            grid(row=0, column=0, padx=10, pady=5, sticky="nsew")
        Button(psu_mode_frame, text="Set", command=lambda: self.set_to_local(),
               width=10).grid(row=0, column=1, pady=5, padx=10, sticky="nsew")
        # Independent / Tracking Mode
        Label(psu_mode_frame, text="Set Operating Mode"). \
            grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        Radiobutton(psu_mode_frame, text='INDEPENDENT mode', value='0', variable=self.psu_operating_mode).grid(
            row=1, column=1, sticky=NSEW)
        Radiobutton(psu_mode_frame, text='TRACKING mode', value='1', variable=self.psu_operating_mode).grid(
            row=2, column=1, sticky=NSEW)
        # Button
        Button(psu_mode_frame, text="Set",
               width=10, command=lambda: self.set_op_mode()).grid(row=3, column=1, pady=5,
                                                                  padx=10, sticky="nsew")
        Label(psu_mode_frame, text="Get Operating Mode"). \
            grid(row=4, column=0, padx=10, pady=5, sticky="nsew")

        Entry(psu_mode_frame, textvariable=self.get_op_status, state='readonly'). \
            grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        Button(psu_mode_frame, text="Get", command=lambda: self.get_operating_mode(),
               width=10).grid(row=5, column=1, pady=5, padx=10, sticky="nsew")
        # Function for Ratio Setting of PSU
        psu_ratio_frame = LabelFrame(self.tab5, text="Ratio")
        psu_ratio_frame.grid(row=1, column=0, padx=(20, 10), pady=(20, 10), sticky="nsew")
        # Value
        Label(psu_ratio_frame, text="Set Ratio").grid(row=0, column=0, padx=10, pady=5,
                                                      sticky="nsew")

        Spinbox(psu_ratio_frame, from_=0, to=100, textvariable=self.set_ratio). \
            grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        Button(psu_ratio_frame, text="Set", command=lambda: self.set_ratio_tracking(),
               width=10).grid(row=1, column=1, pady=5, padx=10, sticky="nsew")
        Label(psu_ratio_frame, text="Get Ratio"). \
            grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        Entry(psu_ratio_frame, textvariable=self.get_ratio, state='readonly'). \
            grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        Button(psu_ratio_frame, text="Get", command=lambda: self.get_ratio_func(),
               width=10).grid(row=3, column=1, pady=5, padx=10, sticky="nsew")

        # Function for the Sizegrip for resizing screen
        # Sizegrip
        ttk.Sizegrip(self.tab1).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))
        ttk.Sizegrip(self.tab2).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))
        ttk.Sizegrip(self.tab3).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))
        ttk.Sizegrip(self.tab4).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))
        ttk.Sizegrip(self.tab5).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

        # Function for Logo Section 5
        lbl_image5 = Label(self.tab5, image=logo)
        lbl_image5.image = logo
        lbl_image5.grid(row=1, column=2, rowspan=3, columnspan=3)
        """
        ******************************************************************************************************
        Compact Daq Controls
        ******************************************************************************************************
        """
        self.tab6 = Frame(tabs)
        tabs.add(self.tab6, text="Compact Daq Controls")

        cDAQ_task1 = LabelFrame(self.tab6, text="Digital Output")
        cDAQ_task1.grid(row=0, column=0, padx=20, pady=20, columnspan=8)
        CDAQ_configuration = LabelFrame(self.tab6, text="CDAQ Configuration")
        CDAQ_configuration.grid(row=1, column=0, padx=20, pady=20)
        cDaq_message = Message(self.tab6, width=400)
        cDaq_message.grid(row=1, column=1, columnspan=6)
        cDaq_message.config(text="This is configured for National Instruments NI cDAQ-9178\n "
                                 "Analog Input Card NI 9205 [cDAQ1Mod1]\n"
                                 "Digital Output Card NI 9485 [cDAQ1Mod2]\n"
                                 "Digital Output Card NI 9485 [cDAQ1Mod3]\n", fg='red')
        self.cDaq_label = Label(CDAQ_configuration, text="Connect to DAQ")
        self.cDaq_label.grid(row=0, column=0, sticky=NSEW)
        Button(CDAQ_configuration, text="Connect", command=self.cdaq_connect).grid(row=0, column=1, padx=20, pady=20,
                                                                                   sticky=NSEW)
        # Output Channels
        self.cdaq_task_output = None
        self.output1 = BooleanVar()
        self.output1.set(True)
        Label(cDAQ_task1, text="Relay 1 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5, padx=5)
        self.output2 = BooleanVar()
        self.output2.set(True)
        Label(cDAQ_task1, text="Relay 2 [cDAQ1Mod2/port0/line1]").grid(row=1, column=0, padx=10, pady=5,
                                                                       sticky="nsew")

        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output2).grid(row=1, column=1, pady=5, padx=5)
        self.output3 = BooleanVar()
        self.output3.set(True)
        Label(cDAQ_task1, text="Relay 3 [cDAQ1Mod2/port0/line2]").grid(row=2, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output3).grid(row=2, column=1, pady=5, padx=5)
        self.output4 = BooleanVar()
        self.output4.set(True)
        Label(cDAQ_task1, text="Relay 4 [cDAQ1Mod2/port0/line3]").grid(row=3, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output4).grid(row=3, column=1, pady=5, padx=5)
        self.output5 = BooleanVar()
        self.output5.set(True)
        Label(cDAQ_task1, text="Relay 5 [cDAQ1Mod2/port0/line4]").grid(row=4, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output5).grid(row=4, column=1, pady=5, padx=5)
        self.output6 = BooleanVar()
        self.output6.set(True)
        Label(cDAQ_task1, text="Relay 6 [cDAQ1Mod2/port0/line5]").grid(row=5, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output6).grid(row=5, column=1, pady=5, padx=5)
        self.output7 = BooleanVar()
        self.output7.set(True)
        Label(cDAQ_task1, text="Relay 7 [cDAQ1Mod2/port0/line6]").grid(row=6, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output7).grid(row=6, column=1, pady=5, padx=5)
        self.output8 = BooleanVar()
        self.output8.set(True)
        Label(cDAQ_task1, text="Relay 8 [cDAQ1Mod2/port0/line7]").grid(row=7, column=0, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output8).grid(row=7, column=1, pady=5, padx=5)
        self.output9 = BooleanVar()
        self.output9.set(True)
        Label(cDAQ_task1, text="Relay 9 [cDAQ1Mod3/port0/line0]").grid(row=0, column=3, padx=10, pady=5,
                                                                       sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output9).grid(row=0, column=4, pady=5, padx=5)
        self.output10 = BooleanVar()
        self.output10.set(True)
        Label(cDAQ_task1, text="Relay 10 [cDAQ1Mod3/port0/line1]").grid(row=1, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output10).grid(row=1, column=4, pady=5, padx=5)
        self.output11 = BooleanVar()
        self.output11.set(True)
        Label(cDAQ_task1, text="Relay 11 [cDAQ1Mod3/port0/line2]").grid(row=2, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output11).grid(row=2, column=4, pady=5, padx=5)
        self.output12 = BooleanVar()
        self.output12.set(True)
        Label(cDAQ_task1, text="Relay 12 [cDAQ1Mod3/port0/line3]").grid(row=3, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output12).grid(row=3, column=4, pady=5, padx=5)
        self.output13 = BooleanVar()
        self.output13.set(True)
        Label(cDAQ_task1, text="Relay 13 [cDAQ1Mod3/port0/line4]").grid(row=4, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output13).grid(row=4, column=4, pady=5, padx=5)
        self.output14 = BooleanVar()
        self.output14.set(True)
        Label(cDAQ_task1, text="Relay 14 [cDAQ1Mod3/port0/line5]").grid(row=5, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output14).grid(row=5, column=4, pady=5, padx=5)
        self.output15 = BooleanVar()
        self.output15.set(True)
        Label(cDAQ_task1, text="Relay 15 [cDAQ1Mod3/port0/line6]").grid(row=6, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output15).grid(row=6, column=4, pady=5, padx=5)
        self.output16 = BooleanVar()
        self.output16.set(True)
        Label(cDAQ_task1, text="Relay 16 [cDAQ1Mod3/port0/line7]").grid(row=7, column=3, padx=10, pady=5,
                                                                        sticky="nsew")
        Checkbutton(cDAQ_task1, text='Turn On', variable=self.output16).grid(row=7, column=4, pady=5, padx=5)
        Button(cDAQ_task1, text="Write", width=10, command=self.digital_output).grid(row=8, column=2, padx=10, pady=10)

        # Analog Input
        self.cdaq_task_input = None
        cDAQ_task2 = LabelFrame(self.tab6, text="Analog Input")
        cDAQ_task2.grid(row=0, column=8, padx=20, pady=20, sticky="nsew")
        self.input1 = StringVar()
        Label(cDAQ_task2, text="Analog Input 1 [cDAQ1Mod1/ai0]").grid(row=0, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input1, state='readonly'). \
            grid(row=0, column=1, padx=10, pady=5, sticky="nsew")
        self.input2 = StringVar()
        Label(cDAQ_task2, text="Analog Input 2 [cDAQ1Mod1/ai1]").grid(row=1, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input2, state='readonly'). \
            grid(row=1, column=1, padx=10, pady=5, sticky="nsew")
        self.input3 = StringVar()
        Label(cDAQ_task2, text="Analog Input 3 [cDAQ1Mod1/ai2]").grid(row=2, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input3, state='readonly'). \
            grid(row=2, column=1, padx=10, pady=5, sticky="nsew")
        self.input4 = StringVar()
        Label(cDAQ_task2, text="Analog Input 4 [cDAQ1Mod1/ai3]").grid(row=3, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input4, state='readonly'). \
            grid(row=3, column=1, padx=10, pady=5, sticky="nsew")
        self.input5 = StringVar()
        Label(cDAQ_task2, text="Analog Input 5 [cDAQ1Mod1/ai4]").grid(row=4, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input5, state='readonly'). \
            grid(row=4, column=1, padx=10, pady=5, sticky="nsew")
        self.input6 = StringVar()
        Label(cDAQ_task2, text="Analog Input 6 [cDAQ1Mod1/ai5]").grid(row=5, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input6, state='readonly'). \
            grid(row=5, column=1, padx=10, pady=5, sticky="nsew")
        self.input7 = StringVar()
        Label(cDAQ_task2, text="Analog Input 7 [cDAQ1Mod1/ai6]").grid(row=6, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input7, state='readonly'). \
            grid(row=6, column=1, padx=10, pady=5, sticky="nsew")
        self.input8 = StringVar()
        Label(cDAQ_task2, text="Analog Input 8 [cDAQ1Mod1/ai7]").grid(row=7, column=0, padx=10, pady=5,
                                                                      sticky="nsew")
        Entry(cDAQ_task2, textvariable=self.input8, state='readonly'). \
            grid(row=7, column=1, padx=10, pady=5, sticky="nsew")
        self.cdaqinput_label = Label(cDAQ_task2, text="This has not been read", fg='red')
        self.cdaqinput_label.grid(row=8, column=1)
        Button(cDAQ_task2, text="Read", width=10, command=lambda: self.create_thread(self.analog_input)). \
            grid(row=9, column=1, padx=10, pady=10)

        # self.output1 = BooleanVar()
        # Label(cDAQ_task1, text="Relay 17 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
        #                                                                sticky="nsew")
        # Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5)
        # self.output1 = BooleanVar()
        # Label(cDAQ_task1, text="Relay 18 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
        #                                                                sticky="nsew")
        # Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5)
        # self.output1 = BooleanVar()
        # Label(cDAQ_task1, text="Relay 19 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
        #                                                                sticky="nsew")
        # Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5)
        # self.output1 = BooleanVar()
        # Label(cDAQ_task1, text="Relay 20 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
        #                                                                sticky="nsew")
        # Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5)
        # self.output1 = BooleanVar()
        # Label(cDAQ_task1, text="Relay 21 [cDAQ1Mod2/port0/line0]").grid(row=0, column=0, padx=10, pady=5,
        #                                                                sticky="nsew")
        # Checkbutton(cDAQ_task1, text='Turn On', variable=self.output1).grid(row=0, column=1, pady=5)

        # Function for Logo Section 6
        lbl_image6 = Label(self.tab6, image=logo)
        lbl_image6.image = logo
        lbl_image6.grid(row=1, column=8, rowspan=3)
        ttk.Sizegrip(self.tab6).grid(row=100, column=100, padx=(0, 5), pady=(0, 5))

    def submission(self, event):
        """
        This is a function that binds the enter key and the enter button\n
        :param event: Button and  Enter Key
        :return: None
        """
        if self.hit is not None and self.user_interface_label.cget('text') == "Active":
            self.button_pressed.set(True)
        elif self.user_interface_label.cget('text') != "Active":
            messagebox.showerror(title="Press Run Error", message="Please Run the Operation")
        else:
            messagebox.showerror(title="HIT Connection Error", message="Please connect to the HIT")

    def user_interface(self):
        """
        This is a function that runs the selected user interfaces\n
        :return: None
        """
        if self.hit is not None and self.method_ran.get() is False:
            self.method_ran.set(True)
            reset_menu(self.gui_psu)
            self.user_interface_label.config(text='Active', foreground="green")
            while True:
                self.txt.config(state='normal')
                [self.txt.insert(END, f'{x}\n\n') for x in self.hit.readBytes().split(f'{CR}{LF}') if x != ""]
                self.txt.yview_moveto(1)
                self.txt.config(state='disabled')
                time.sleep(1)
                # self.button.wait_variable(self.button_pressed)
                # self.button_pressed.set("haha")
                if self.button_pressed.get():
                    user = self.user_input.get()
                    self.button_pressed.set(False)
                    user_text = f'{user}{CR}{LF}'.encode(encode_style)
                    self.txt.config(state='normal')
                    self.txt.insert(END, f'{user}\n\n')
                    self.txt.config(state='disabled')
                    self.hit.ser.write(user_text)
                    if user.lower().strip(" ") == 'stop':
                        self.user_interface_label.config(text='Finished', foreground="red")
                        break

            self.method_ran.set(False)
        elif self.method_ran.get():
            messagebox.showerror(title="Function already running", message="You need to wait for the other function "
                                                                           "that is running to finish running")
        else:
            messagebox.showerror(title="HIT Connection Error", message="Please connect to the HIT")

    def funcExit(self) -> None:
        """
        This is a method that is used for the exiting of the App\n
        :return: None
        """
        mbox = messagebox.askquestion(title="Exit", message='Are you sure you want to exit', icon='warning')
        if mbox == 'yes':
            self.destroy()

    def configuration(self) -> None:
        """
        This is a function for the creation of the configuration window\n
        :return: None
        """
        toplevel: Toplevel = Toplevel(self, height=500, width=500)
        # Label Frame
        configArea: LabelFrame = LabelFrame(toplevel, text='Configuration')
        configArea.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Combo Box

        comports1 = [comport.device for comport in serial.tools.list_ports.comports()]
        comports2 = [comport.device for comport in serial.tools.list_ports.comports()]
        # TTiPSU
        Label(configArea, text="Connect To TTiPSU").grid(row=0, column=0, columnspan=4, padx=10, sticky="nsew")
        Label(configArea, text="COM Port").grid(row=1, column=0, sticky="nsew")
        ttk.Combobox(configArea, textvariable=self.comPort1, values=comports1, state='readonly'). \
            grid(row=1, column=1, padx=10, sticky="nsew")
        # HIT
        Label(configArea, text="Connect To HIT").grid(row=2, column=0, columnspan=4, padx=10, sticky="nsew")
        Label(configArea, text="COM Port").grid(row=3, column=0, pady=5, sticky="nsew")
        ttk.Combobox(configArea, textvariable=self.comPort2, values=comports2, state='readonly'). \
            grid(row=3, column=1, padx=10, pady=10, sticky="nsew")
        # Baudrate
        Label(configArea, text="Baudrate").grid(row=4, column=0, pady=5, padx=10, sticky="nsew")
        baudrate_entry: Entry = Entry(configArea, width=30)
        baudrate_entry.grid(row=4, column=1, padx=10, sticky="nsew")
        baudrate_entry.insert(0, '115200')
        # Parity
        Label(configArea, text="Parity").grid(row=5, column=0, pady=5, sticky="nsew")
        parity_entry: Entry = Entry(configArea, width=30)
        parity_entry.grid(row=5, column=1, padx=10, sticky="nsew")
        parity_entry.insert(0, 'N')
        # Stopbits
        Label(configArea, text="Stopbits").grid(row=6, column=0, pady=5, sticky="nsew")
        stopbits_entry: Entry = Entry(configArea, width=30)
        stopbits_entry.grid(row=6, column=1, padx=10, sticky="nsew")
        stopbits_entry.insert(0, '1')
        # Bytesize
        Label(configArea, text="Bytesize").grid(row=7, column=0, pady=5, padx=10, sticky="nsew")
        bytesize_entry: Entry = Entry(configArea, width=30)
        bytesize_entry.grid(row=7, column=1, padx=10, sticky="nsew")
        bytesize_entry.insert(0, '8')
        # Timeout
        Label(configArea, text="Timeout").grid(row=8, column=0, pady=5, padx=10, sticky="nsew")
        timeout_entry: Entry = Entry(configArea, width=30)
        timeout_entry.grid(row=8, column=1, padx=10, sticky="nsew")
        timeout_entry.insert(0, '1')
        # InterByteTimeout
        Label(configArea, text="InterByteTimeout").grid(row=9, column=0, pady=5, sticky="nsew")
        inter_byte_timeout_entry = Entry(configArea, width=30)
        inter_byte_timeout_entry.grid(row=9, column=1, padx=10, sticky="nsew")
        inter_byte_timeout_entry.insert(0, '0.1')
        # Button
        Button(configArea,
               text="Connect",
               command=lambda: self.connect_configuration(toplevel=toplevel,
                                                          baudrate=int(baudrate_entry.get()),
                                                          parity=parity_entry.get(),
                                                          stopbits=int(stopbits_entry.get()),
                                                          bytesize=int(bytesize_entry.get()),
                                                          timeout=int(timeout_entry.get()),
                                                          interbytetimeout=float(
                                                              inter_byte_timeout_entry.get()))).grid(row=10, column=2,
                                                                                                     columnspan=3,
                                                                                                     padx=10, pady=5,
                                                                                                     sticky="nsew")
        toplevel.grab_set()

    def connect_configuration(self, toplevel, baudrate=None, parity=None,
                              stopbits=None, bytesize=None, timeout=None, interbytetimeout=None):
        """
        This is the function that connects the HIT and the PSU to the comports\n
        :param toplevel:
        :param baudrate:
        :param parity:
        :param stopbits:
        :param bytesize:
        :param timeout:
        :param interbytetimeout:
        :return:
        """
        self.baudrate = baudrate
        self.parity = parity
        self.stopbits = stopbits
        self.bytesize = bytesize
        self.timeout = timeout
        self.inter_byte_timeout = interbytetimeout
        if (not isinstance(self.hit, HIT_Interface) or self.hit is None) and baudrate is not None:
            try:
                if isinstance(self.gui_psu, TtiPsu):
                    del self.gui_psu
                self.hit = HIT_Interface(comport_psu=self.comPort1.get(),
                                         comport_hit=self.comPort2.get(),
                                         baudrate=self.baudrate,
                                         parity=self.parity,
                                         stopbits=self.stopbits,
                                         bytesize=self.bytesize,
                                         timeout=self.timeout,
                                         interbytetimeout=self.inter_byte_timeout)
                self.gui_psu = self.hit.psu
            except TtiPsuException:
                messagebox.showerror(title="Power Supply Error", message="The selected COM port for the power supply "
                                                                         "is incorrect. Please select a different "
                                                                         "COM Port")
            except serial.SerialException:
                messagebox.showerror(title="HIT Serial Connection Error",
                                     message='There was an error in connecting to the COM Port specified. Try closing '
                                             'another program or Putty. You may be trying to open COM port that is '
                                             'open in another program')
            else:
                if toplevel is not None:
                    toplevel.destroy()
                messagebox.showinfo(title="Successfully Connected",
                                    message="You successfully connected to the COM Port")
        elif not isinstance(self.gui_psu, TtiPsu) or self.gui_psu is None:
            try:
                self.gui_psu = TtiPsu(self.comPort1.get())
            except TtiPsuException:
                messagebox.showerror(title="Power Supply Error", message="The selected COM port for the power supply "
                                                                         "is incorrect. Please select a different "
                                                                         "COM Port")
            else:
                if toplevel is not None:
                    toplevel.destroy()
                messagebox.showinfo(title="Successfully Connected",
                                    message="You successfully connected to the COM Port")
        else:
            if toplevel is not None:
                toplevel.destroy()
            messagebox.showinfo(title="Already Connected", message="You are already connected to the system")

    def reading_data(self) -> None:
        """
        This is a function that is used to read the data\n
        :return: None
        """
        path = Path(self.csvFile.get())
        absPath = str(path.parent.absolute())
        dirPath = '\\'.join(absPath.split('\\')[0:-1])
        relPath = f'{dirPath}\\CSVs\\{self.csvFile.get()}'
        try:
            self.pt.importCSV(relPath)
            self.pt.autoResizeColumns()
            self.pt.show()
        except FileNotFoundError:
            messagebox.showerror(title='FileNotFound',
                                 message="Please select a file from the given list of CSVs files")

    def create_thread(self, function) -> None:
        """
        This is a function for the creation of threads\n
        :param function:
        :return: None
        """
        t1 = threading.Thread(target=function)
        self.threads.append(t1)
        for thread in self.threads:
            if thread == t1 and not thread.is_alive():
                thread.start()

    def processing_threads(self, function) -> None:
        """
        This is a function for the processing of threads\n
        :param function: Any Function
        :return: None
        """
        try:
            new_thread = threading.Thread(target=function)
            self.threads.append(new_thread)
            for thread in self.threads:
                if thread == new_thread and not thread.is_alive():
                    thread.start()
                    thread.join()
        except AttributeError:
            messagebox.showerror(title="Configure System", message="You need to configure the system if you "
                                                                   "want to run a new test")

    def run_interface(self) -> None:
        """
        This is a function for the running of interfaces\n

        :return: None
        """
        selected_item = self.interface_listBox.curselection()
        if (selected_item != () and self.hit is not None) and self.method_ran.get() is False:
            self.method_ran.set(True)
            for item in selected_item:
                time.sleep(1)
                function = getattr(self.hit, self.interface_listBox.get(item))
                self.interface_tracker_label.config(text=f"{self.interface_listBox.get(item)} is in progress",
                                                    foreground='green')
                self.processing_threads(function)
                self.interface_tracker_label.config(text=f"{self.interface_listBox.get(item)} has Finished",
                                                    foreground='red')

                prefix = self.interface_listBox.get(item).split("_")[0]
                self.csvFile.set(f'{prefix}.csv')
                self.reading_data()
            self.method_ran.set(False)
        elif self.hit is None:
            messagebox.showerror(title="Connect to Device", message="You need to connect to the device")
        elif self.method_ran.get():
            messagebox.showerror(title="Function already running", message="You need to wait for the other function "
                                                                           "that is running to finish running")
        else:
            messagebox.showerror(title="No Interface Selected", message="Please select a function to run. You "
                                                                        "did not select a Interface")

    def test_interface(self) -> None:
        """
        This is a function for the running of the test interface\n

        :return: None
        """
        selected_item = self.testBox.curselection()
        if (selected_item != () and self.hit is not None) and self.method_ran.get() is False:
            self.method_ran.set(True)
            del self.hit
            lst = []
            for item in selected_item:
                function = self.testBox.get(item)
                for x, y in zip(self.name, sum(self.classes, [])):
                    try:
                        getattr(getattr(getattr(Tests, x), y), function)
                        lst.append(find_path(f'{x}.py::{y}::{function}'))
                    except AttributeError:
                        pass
            # lst.append('-v')
            lst.append('--verbose')
            lst.append(f'--session2file={self.dirPath}\\out.txt')

            self.test_tracker_label.config(text="Tests are in progress.\nResults will show when Tests are finished",
                                           foreground='blue')
            self.processing_threads(lambda: pytest.main(lst))
            self.txt1.config(state='normal')
            with open(f'{self.dirPath}\\out.txt', 'r') as f:
                self.txt1.insert(END, f.read())
            self.txt1.config(state='disabled')
            self.method_ran.set(False)
            self.test_tracker_label.config(text="Tests are finished. Check Console for results", foreground='green')
            self.comPort1.set('COM4')
            self.comPort2.set('COM5')
            self.hit = None
            self.connect_configuration(toplevel=None,
                                       baudrate=int(self.baudrate),
                                       parity=self.parity,
                                       stopbits=int(self.stopbits),
                                       bytesize=int(self.bytesize),
                                       timeout=int(self.timeout),
                                       interbytetimeout=float(
                                           self.inter_byte_timeout))
        elif self.hit is None:
            messagebox.showerror(title="Connect to Device", message="You need to connect to the device")
        elif self.method_ran.get():
            messagebox.showerror(title="Function already running", message="You need to wait for the other function "
                                                                           "that is running to finish running")
        else:
            messagebox.showerror(title="No Function Selected", message="Please select a test to run. You "
                                                                       "did not select a test")

    def connect_psu(self) -> None:
        """
        This is a function for connecting to the PSU\n
        :return: None
        """
        toplevel = Toplevel(self, height=500, width=500)
        # Label Frame
        configArea = LabelFrame(toplevel, text='Connect to PSU')
        configArea.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Combo Box
        comports1 = [comport.device for comport in serial.tools.list_ports.comports()]
        # TTiPSU
        title_psu = Label(configArea, text="Connect To TTiPSU")
        title_psu.grid(row=0, column=0, columnspan=4, padx=10, sticky="nsew")
        com_label1 = Label(configArea, text="COM Port")
        com_label1.grid(row=1, column=0, sticky="nsew")
        comboBox1 = ttk.Combobox(configArea, textvariable=self.comPort1, values=comports1, state='readonly')
        comboBox1.grid(row=1, column=1, padx=10, sticky="nsew")
        # Button
        button = Button(configArea, text="Connect",
                        command=lambda: self.connect_configuration(toplevel=toplevel))
        button.grid(row=10, column=2, columnspan=3, padx=10, pady=5, sticky="nsew")
        toplevel.grab_set()

    def psu_voltage_change(self) -> None:
        """
        This is a helper function or the changing of voltage\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.psu_channel.get())
                state = self.output_state.get()
                if state:
                    channel.set_output_state(TtiPsuChannelState.On)
                else:
                    channel.set_output_state(TtiPsuChannelState.Off)
                channel.set_voltage(float(self.set_voltage.get()))
                channel.set_current(float(self.set_current.get()))
            except AttributeError:
                messagebox.showerror(title="Make A Selection", message="Please select a given channel "
                                                                       "that you want to control")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def psu_get_info(self) -> None:
        """
        This is a function for getting the into of the PSU Basic Controls\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.psu_get_channel.get())
                self.get_voltage.set(channel.get_voltage())
                self.get_current.set(channel.get_current())
                self.get_output_state.set(channel.get_output_state())
            except AttributeError:
                messagebox.showerror(title="Make A Selection", message="Please select a given channel "
                                                                       "that you want to control")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def adv_set_volt(self) -> None:
        """
        This is a function for the setting of PSU Advanced Controls\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.adv_psu_channel.get())
                voltage_method = self.psu_adv_set_volt.get()
                value = self.set_adv_volts.get()
                time_interval = self.adv_volts_interval.get()
                verify = self.adv_verify_volt.get()  # Verify doesnt work Bug fix
                if voltage_method == 'set_voltage_trip':
                    channel.set_voltage_trip(value)
                elif voltage_method == 'set_voltage_delta':
                    try:
                        inc_dec = int(self.psu_volts_inc_dec.get())
                        channel.set_voltage_delta(value)
                        if inc_dec:
                            channel.set_voltage_inc(verify)
                        else:
                            channel.set_voltage_dec(verify)
                    except ValueError:
                        messagebox.showerror(title="Chosen Inc/Dec Option",
                                             message="Select Decrement or Increment Voltage Options")
                elif voltage_method == 'set_voltage_and_wait':
                    channel.set_voltage_and_wait(value=value, interval=time_interval)
                else:
                    messagebox.showerror(title="select Voltage Method", message="You did not select a voltage method. "
                                                                                "Please select one")

            except AttributeError:
                messagebox.showerror(title="Make A Selection", message="Please select a given channel "
                                                                       "that you want to control")
            except pyvisa.errors.VisaIOError:
                messagebox.showerror(title='Timeout', message="The given command made the system timeout")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def psu_adv_volt_get_info(self) -> None:
        """
        This is a function for the getting volt info in Advance section\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.psu_adv_get_volt_channel.get())
                self.adv_get_volt_readback.set(channel.get_voltage_readback())
                self.adv_get_voltage.set(channel.get_voltage_trip())
                self.adv_get_volt_delta.set(channel.get_voltage_delta())
            except AttributeError:
                messagebox.showerror(title="Make A Selection", message="Please select a given channel "
                                                                       "that you want to control")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def psu_adv_curr_get_info(self) -> None:
        """
        This is a function for the getting info current advance section\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.psu_adv_get_curr_channel.get())
                self.adv_get_curr_readback.set(channel.get_current_readback())
                self.adv_get_current.set(channel.get_current_trip())
                self.adv_get_curr_delta.set(channel.get_current_delta())
            except AttributeError:
                messagebox.showerror(title="Make A Selection",
                                     message="Please select a given channel that you want to control")
        else:
            messagebox.showerror(title="PSU Connection Error",
                                 message="Please connect to the PSU")

    def adv_set_curr(self) -> None:
        """
        This is a function for the setting of the current in advance section\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                channel = getattr(self.gui_psu, self.adv_psu_curr_channel.get())
                current_method = self.psu_adv_set_curr.get()
                value = float(self.set_adv_curr.get())
                if current_method == 'set_current_trip':
                    channel.set_current_trip(value)
                elif current_method == 'set_current_delta':
                    try:
                        inc_dec = int(self.psu_curr_inc_dec.get())

                        channel.set_current_delta(value)
                        if inc_dec:
                            channel.set_current_inc()
                        else:
                            channel.set_current_dec()
                    except ValueError:
                        messagebox.showerror(title="Chosen Inc/Dec Option",
                                             message="Select Decrement or Increment Current Options")
                else:
                    messagebox.showerror(title="select Current Method", message="You did not select a voltage method. "
                                                                                "Please select one")
            except AttributeError:
                messagebox.showerror(title="Make A Selection", message="Please select a given channel "
                                                                       "that you want to control")
            except pyvisa.errors.VisaIOError:
                messagebox.showerror(title='Timeout', message="The given command made the system timeout")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def set_to_local(self) -> None:
        """
        This is a function that sets the PSU to local mode\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.set_to_local()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def get_interface_lock(self) -> None:
        """
        This is a function that gets the interface lock status of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            lock_status = str(self.gui_psu.get_interface_lock())
            self.lock_status.set(lock_status)
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def set_output_all(self) -> None:
        """
        This is a function that sets the output of both channels of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:

            if self.output_all.get():
                self.gui_psu.set_output_all(TtiPsuChannelState.On)
            else:
                self.gui_psu.set_output_all(TtiPsuChannelState.Off)
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def set_op_mode(self) -> None:
        """
        This is a function that sets the operating mode of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            mode = self.psu_operating_mode.get()
            if mode:
                self.gui_psu.set_operating_mode(TtiPsuOutputMode.Tracking)
            else:
                self.gui_psu.set_operating_mode(TtiPsuOutputMode.Independent)
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def set_ratio_tracking(self) -> None:
        """
        This is a method that sets the ratio of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            try:
                ratio = int(self.set_ratio.get())
                if ratio >= 0 or ratio <= 100:
                    self.gui_psu.set_ratio_tracking(ratio)
                else:
                    raise ValueError
            except ValueError:
                messagebox.showerror(title="Incorrect Value",
                                     message="Please select an integer value between 1 and 100")
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def get_ratio_func(self) -> None:
        """
        This is a function for getting the ration of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            ratio = self.gui_psu.get_ratio()
            self.get_ratio.set(str(ratio))
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def get_operating_mode(self) -> None:
        """
        This is a helper function for getting the Operating Mode of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            op_mode = self.gui_psu.get_operating_mode()
            self.get_op_status.set(str(op_mode))

        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def device_settings_reset(self) -> None:
        """
        This is a function that resets the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.device_settings_reset()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def reset_user_interface(self) -> None:
        """
        This is a function that resets the menu for the user interface\n
        :return: None
        """
        if (self.gui_psu is not None and self.hit is not None) and self.user_interface_label.cget('text') == 'Active':
            reset_menu(self.gui_psu)
        elif self.gui_psu is None:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")
        else:
            messagebox.showerror(title="HIT Connection Error", message="Please connect to the HIT")

    def stop_user_interface(self) -> None:
        """
        This is a function that stops the user interface and allows the user to copy the data from the text box\n
        :return: None
        """
        if (self.gui_psu is not None and self.hit is not None) and self.user_interface_label.cget('text') == 'Active':
            self.button_pressed.set(True)
            self.user_input.set("stop")
        elif self.gui_psu is None:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")
        elif self.method_ran.get():
            messagebox.showerror(title="Function already running", message="You need to wait for the other function "
                                                                           "that is running to finish running")
        else:
            messagebox.showerror(title="HIT Connection Error", message="Please connect to the HIT")

    def clear(self) -> None:
        """
        This is a function that clears the user interface text box\n
        :return: None
        """
        self.txt.config(state='normal')
        self.txt.delete('1.0', END)
        self.txt.config(state='disabled')

    def set_interface_lock(self) -> None:
        """
        This is a function that sets the interface lock for the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.set_interface_lock()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def release_lock(self) -> None:
        """
        This is a function that releases the interface lock of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.set_interface_lock()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def reset_trip_condition(self):
        """
        This is a function that resets the trip conditions of the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.set_interface_lock()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def release_limit_lock(self):
        """
        This is a function that releases the limit lock on the PSU\n
        :return: None
        """
        if self.gui_psu is not None:
            self.gui_psu.set_interface_lock()
        else:
            messagebox.showerror(title="PSU Connection Error", message="Please connect to the PSU")

    def digital_output(self):
        """
        This is a function that write the digital output to the DAQ cards NI 9485\n
        :return: None
        """
        if self.cdaq_task_input is not None and self.cdaq_task_output is not None:
            lst = [self.output1.get(), self.output2.get(), self.output3.get(), self.output4.get(), self.output5.get(),
                   self.output6.get(), self.output7.get(), self.output8.get(), self.output9.get(), self.output10.get(),
                   self.output11.get(), self.output12.get(), self.output13.get(), self.output14.get(),
                   self.output15.get(),
                   self.output16.get()]
            self.cdaq_task_output.cDaqTask.write(lst)
        else:
            messagebox.showerror(title="CDaq Connection Error", message="Please connect to the DAQ")

    def analog_input(self):
        """
        This is a function that reads the analog input from the DAQ cards NI 9205 in a loop fashion\n
        :return: None
        """
        if (self.cdaq_task_input is not None and self.cdaq_task_output is not None) and self.cdaqinput_label.cget(
                'text') != 'Active':
            self.cdaqinput_label.config(text="Active", fg='green')
            while 1:
                self.input1.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[0])
                self.input2.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[1])
                self.input3.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[2])
                self.input4.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[3])
                self.input5.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[4])
                self.input6.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[5])
                self.input7.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[6])
                self.input8.set(self.cdaq_task_input.cDaqTask.read(number_of_samples_per_channel=1)[7])
                time.sleep(1)
        elif self.cdaqinput_label.cget('text') != 'Active':
            messagebox.showerror(title="Active Error", message="The system is already reading the data")
        else:
            messagebox.showerror(title="CDaq Connection Error", message="Please connect to the DAQ")

    def cdaq_connect(self) -> None:
        """
        This is a function that connects the DAQ to the GUI\n
        :return: None
        """
        if self.cdaq_task_input is None and self.cdaq_task_output is None:
            self.cdaq_task_output = cDaq()
            self.cdaq_task_output.ConfigOutputs()

            self.cdaq_task_input = cDaq()
            self.cdaq_task_input.ConfigInputs()
            messagebox.showinfo(title="Connected", message="You are connected to the DAQ")
        else:
            messagebox.showerror(title="CDaq Connection Error", message="Please connect to the DAQ")

    def select_all(self) -> None:
        """
        This is a method that allows you to select all the interfaces in the GUI\n
        :return: None
        """
        if self.interface_checkbutton.get():
            self.interface_listBox.select_set(0, END)
            self.interface_listBox.event_generate("<<ListboxSelect>>")
        else:
            self.interface_listBox.select_clear(0, END)
            self.interface_listBox.event_generate("<<ListboxSelect>>")

    # def interface_listBox_selection(self, event):
    #     self.interface_checkbutton.set(True)

    def test_select_all(self) -> None:
        """
        This is a method that allows you to select all the tests in the GUI\n
        :return: None
        """
        if self.testing_checkbutton.get():
            self.testBox.select_set(0, END)
            self.testBox.event_generate("<<ListboxSelect>>")
        else:
            self.testBox.select_clear(0, END)
            self.testBox.event_generate("<<ListboxSelect>>")

    def reset_test_interface(self):
        """
        This is a function that resets the test interface by resetting the menu\n
        :return: None
        """
        self.txt1.config(state='normal')
        self.txt1.delete('1.0', END)
        self.txt1.config(state='disabled')


if __name__ == "__main__":
    app = App()
    app.mainloop()

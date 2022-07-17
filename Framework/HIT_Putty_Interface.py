"""
This code was developed by Rasheed Martin in 2022 as a Firmware Engineering Intern located in the
Milwaukee, Wisconsin headquarters. The purpose of the code is to interact with the
Hard Integration Test Device
"""

from pathlib import Path
from time import time

import pandas as pd
import serial

from Framework.TtiPsu import *


def reset_menu(psu: TtiPsu):
    psu.Channel1.set_voltage(24)
    psu.Channel1.set_current(.1)
    psu.Channel1.set_output_state(TtiPsuChannelState.Off)
    time.sleep(.5)
    psu.Channel1.set_output_state(TtiPsuChannelState.On)
    time.sleep(.5)


def write_read(datafile: str, lst: dict, index, message: str = "") -> None:
    """
    This is a helper method to write and read from a CSV file\n
    :param index:
    :param datafile: The file extension of the CSV file
    :param lst: The dictionary resulting from the interface from which it is called
    :param message: Optional[Title of data or Message for the data]
    :return: None
    """

    data = pd.DataFrame(lst, index=index)
    path = Path(datafile)
    absPath = str(path.parent.absolute())
    dirPath = '\\'.join(absPath.split('\\')[0:-1])
    relPath = f'{dirPath}\\CSVs\\{datafile}'
    try:
        data.to_csv(relPath, index=False)
    except OSError:
        relPath = f'{dirPath}\\Rasheedattempt\\CSVs\\{datafile}'
        data.to_csv(relPath, index=False)
    df = pd.read_csv(relPath, index_col=[0])
    print(message)
    with pd.option_context('display.max_rows', None, 'display.max_columns', None):
        print(df)


CR = '\r'
LF = '\n'
encode_style = 'ASCII'


class HIT_Interface:

    def __init__(self, comport_psu, comport_hit, baudrate=115200, parity=serial.PARITY_NONE,
                 stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=1, interbytetimeout=0.1):
        try:
            self.ser = serial.Serial(
                port=comport_hit,  # Change this hardcoded COM Port
                baudrate=baudrate,
                parity=parity,
                stopbits=stopbits,
                bytesize=bytesize,
                timeout=timeout,
                inter_byte_timeout=interbytetimeout)
            self.psu = TtiPsu(comport_psu)
        except serial.SerialException:
            print(f'There was an error in connecting to the COM Port specified. Try closing another program or Putty. '
                  f'You may be trying to open COM port that is open in another program')
            raise serial.SerialException

        else:
            print("You successfully connected to the COM Port")

    def __del__(self):
        self.ser.close()
        self.psu.__del__()

    def readBytes(self) -> str:
        """
        This is a helper function that is reading bytes from the buffer in an efficient way
        :return: The text from the buffer after being decoded
        """
        while True:
            # Reads one byte of information
            myBytes = self.ser.read(1)
            # Checks for more bytes in the input buffer
            bufferBytes = self.ser.inWaiting()
            # If exists, it is added to the myBytes variable with previously read information
            if bufferBytes:
                myBytes = myBytes + self.ser.read(bufferBytes)
            if myBytes is not None:
                return myBytes.decode(encode_style)

    def _interfacing_menu(self, test_suite, test_type, loops=None, delay_per_cycle=None):
        reset_menu(self.psu)
        self.readBytes()
        self.ser.write(f'{test_suite}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        self.readBytes()
        self.ser.write(f'{test_type}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        if loops is not None:
            self.readBytes()
            self.ser.write(f'{str(loops)}{CR}{LF}'.encode(encode_style))
            time.sleep(1)
        if delay_per_cycle is not None:
            self.readBytes()
            self.ser.write(f'{str(delay_per_cycle)}{CR}{LF}'.encode(encode_style))
            time.sleep(5)

    def adc_user_interface(self, loops: int = 20, delay_per_cycle: int = 20) -> dict:
        """
        This is a method that allows you to retrieve data from the ADC interface from the
        Digital Input/Output Test Suite
        :param loops: The amount of times the test is looped
        :param delay_per_cycle: The amount of delays per cycle of loop
        :return: A dictionary of the data from the test
        """
        test_suite = '1'
        test_type = 'adc'
        datafile = 'adc.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
            lst = {}
            title = []
            count = 0
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.strip().split(",")
                if i == 1:
                    data = " ".join(data)
                    data = data.split(" ")
                    for y in data:
                        if y != '':
                            title.append(y)
                            lst[title[count]] = []
                            count += 1
                elif len(data) == 1:
                    continue
                else:
                    for idx, y in enumerate(lst.keys()):
                        lst[y].append(data[idx].strip())
            if lst != "" and lst != {}:
                break
        # Write to CSV file and print the dataframe
        write_read(datafile=datafile, lst=lst, index=None)
        return lst

    def digital_user_interface(self, loops: int = 20, delay_per_cycle: int = 20) -> dict:
        """
        This is a method that allows you to retrieve data from the digital interface from the
        Digital Input/Output Test Suite
        :param loops: The amount of times the test is looped
        :param delay_per_cycle: The amount of delays per cycle of loop
        :return: A dictionary of the data from the test
        """
        test_suite = '1'
        test_type = 'digital'
        datafile = 'digital.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
            lst = {}
            title = []
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(",")
                if i == 1:
                    for idx, y in enumerate(data):
                        title.append(y)
                        lst[title[idx]] = []
                elif len(data) == 1:
                    continue
                elif len(data) >= 4:
                    data.pop()
                    for y, z in zip(title, data):
                        lst[y].append(z.strip())
            if lst != "" and lst != {}:
                break
        # Write to CSV file and print the dataframe
        write_read(datafile=datafile, lst=lst, index=None)
        return lst

    def switch_user_interface(self, loops: int = 20, delay_per_cycle: int = 20) -> dict:
        """
        This is a method that allows you to retrieve data from the switch interface from the
        Digital Input/Output Test Suite
        :param loops: The amount of times the test is looped
        :param delay_per_cycle: The amount of delays per cycle of loop
        :return: A dictionary of the data from the test
        """
        test_suite = '1'
        test_type = 'switch'
        datafile = 'switch.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
            lst = {}
            title = ""
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(",")
                if i == 1:
                    title = data[0]
                    lst[title] = []
                elif len(data) == 1:
                    continue
                else:
                    data.pop()
                    lst[title].append(data[0].strip())
            if lst != "" and lst != {}:
                break
        # Write to CSV file and print the dataframe
        write_read(datafile=datafile, lst=lst, index=None)

        return lst

    def temp_user_interface(self, loops: int = 20, delay_per_cycle: int = 20) -> dict:
        """
        This is a method that will work but is buggy based on the Binary Code on the machine. Needs to be fixed.
        :param loops:
        :param delay_per_cycle:
        :return:
        """
        raise NotImplementedError
        # test_suite = '1'
        # test_type = 'temp'
        # self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
        # lst = {'InternalTempRaw': [], 'InternalTempInDegC': []}
        #
        # for x in self.ser.read_all().decode("ASCII").split("\r\n"):
        #     data = x.split(",")
        #     print(data)
        #     if len(data) == 1:
        #         continue
        #     else:
        #         lst['InternalTempRaw'].append(data[0])
        #         lst['InternalTempInDegC'].append(data[1])
        #
        # return lst

    def snapshot_user_interface(self) -> tuple[dict, str]:
        test_suite = '1'
        test_type = 'snapshot'
        datafile = 'snapshot.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
            lst = {}
            count = 0
            title = " "
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split("=")
                if i == 1:
                    title = data[0]
                elif len(data) == 1:
                    continue
                else:
                    lst[data[0]] = data[1]
            if lst != "" and lst != {}:
                break
        # Write to CSV file and print the dataframe
        write_read(datafile=datafile, lst=lst, index=[0])

        return lst, title

    """
    Memory and Revision Test Suite
    """

    def version_user_interface(self) -> dict:
        """
        This is a test to see the firmware version
        :return:
        """
        test_suite = '2'
        test_type = 'version'
        datafile = 'version.csv'
        lst = {}
        while True:
            self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(":")
                print(data)
                if i == 1:
                    lst[data[0]] = data[1]

            if lst != "" and lst != {}:
                break

        write_read(datafile=datafile, lst=lst, index=[0])

        return lst

    def stack_user_interface(self) -> tuple[dict, str]:
        """
        This is a test to see the stack and heap usage
        :return:
        """
        test_suite = '2'
        test_type = 'stack'
        datafile = 'stack.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
            lst = {}
            message = ""
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(":")
                if i == 1:
                    message = data[0]
                elif len(data) == 1:
                    continue
                else:
                    lst[data[0]] = data[1]
            if lst != "" and lst != {}:
                break

        write_read(datafile=datafile, lst=lst, index=[0])

        return lst, message

    def allocator_user_interface(self):
        """
        I am not able to get a response from the machine. This method needs to be looked at again
        :return:
        """
        raise NotImplementedError

    """
    DB, EE, Watchdog and RNG
    """

    def eeprom_user_interface(self) -> tuple[dict, str]:
        """

        :return:
        """
        test_suite = '3'
        test_type = 'eeprom'
        datafile = 'eeprom.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
            lst = {}
            title = []
            message = ""
            time.sleep(2)
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(",")
                if i == 1:
                    for idx, y in enumerate(data):
                        title.append(y)
                        lst[title[idx]] = []
                elif i == 74:
                    message = data[0]
                elif len(data) == 1:
                    pass
                else:
                    for y, z in zip(title, data):
                        lst[y].append(z.strip())
            if lst != "" and lst != {}:
                break

        write_read(datafile=datafile, lst=lst, index=None)

        return lst, message

    def fast_iwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'fast_iwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def slow_iwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'slow_iwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def fast_wwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'fast_wwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}\r\n'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def slow_wwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'slow_wwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def watchdog_reset_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'reset'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def hard_reset_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'hard'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def soft_reset_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'soft'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def stop_iwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'stop_iwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}{CR}{LF}'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def stop_wwdg_user_interface(self):
        test_suite = '3'
        test_type = 'watchdog'
        command = 'stop_wwdg'
        self._interfacing_menu(test_suite, test_type, loops=None, delay_per_cycle=None)
        [print(x) for x in self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')]
        self.ser.write(f'{command}\r\n'.encode(encode_style))
        time.sleep(1)
        for i, x in enumerate(self.ser.read_all().decode(encode_style).split(f'{CR}{LF}')):
            data = x.split(",")
            if data == 'Enter Test-> ':
                print("Successful")

        raise NotImplementedError

    def rng_user_interface(self, loops: int = 40, delay_per_cycle: int = 13) -> tuple[dict, list]:
        test_suite = '3'
        test_type = 'rng'
        datafile = 'rng.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
            lst = {}
            title = []
            message = []
            time.sleep(4)
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(",")
                if i == 2:
                    for idx, y in enumerate(data):
                        title.append(y)
                        lst[title[idx]] = []
                elif i in (28, 29, 30):
                    message.append(data[0])
                elif len(data) == 1:
                    pass
                else:
                    for y, z in zip(title, data):
                        lst[y].append(z.strip())
            if lst != "" and lst != {}:
                break

        write_read(datafile=datafile, lst=lst, index=None)

        return lst, message

    """
    Gain Control TBD
    """

    def trip_user_interface(self, trip_code: int, trip_LED_Code: int):
        """
        This needs more thinking of how to verify that a LED is blinking
        :param trip_code:
        :param trip_LED_Code:
        :return:
        """
        test_suite = '5'
        test_type = 'trip'
        trip_code = 4  # (1...255)
        trip_LED_Code = 5  # (1...255)
        raise NotImplementedError

    def warning_user_interface(self, warning_code: int, warning_LED_Code: int):
        """
        This needs more thinking of how to verify that a LED is blinking
        :param warning_LED_Code:
        :param warning_code:
        :return:
        """
        test_suite = '5'
        test_type = 'trip'
        warning_code = 4  # (1...255)
        warning_LED_Code = 5  # (1...255)
        raise NotImplementedError

    def noise_user_interface(self, phase_number: int):
        """
        This is buggy and needs to be reworked.
        :param phase_number:
        :return:
        """
        test_suite = '6'
        test_type = 'noise'
        phase_number = 2  # (1...3, 0 for all)
        raise NotImplementedError

    def bucket_user_interface(self, loops: int = 40, delay_per_cycle: int = 13) -> dict:
        """
        This is buggy and needs to be reworked.
        :param delay_per_cycle:
        :param loops:
        :return:
        """
        test_suite = '6'
        test_type = 'bucket'
        datafile = 'bucket.csv'
        while True:
            self._interfacing_menu(test_suite, test_type, loops, delay_per_cycle)
            lst = {}
            title = []
            time.sleep(4)
            for i, x in enumerate(self.readBytes().split(f'{CR}{LF}')):
                data = x.split(",")
                if i == 6:
                    for idx, y in enumerate(data):
                        title.append(y)
                        lst[title[idx]] = []
                elif len(data) == 1:
                    pass
                else:
                    for y, z in zip(title, data):
                        lst[y].append(z.strip())
            if lst != "" and lst != {}:
                break
        # Write this data to a file
        write_read(datafile=datafile, lst=lst, index=None)

        return lst


if __name__ == "__main__":
    # hit = HIT_Interface()
    # hit.user_interaction()
    print(input("Enter your answer"))

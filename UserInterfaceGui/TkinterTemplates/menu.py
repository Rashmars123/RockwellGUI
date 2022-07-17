from tkinter import *
from tkinter import messagebox
root = Tk()


def funcExit():
    mbox = messagebox.askquestion(title="Exit", message='Are you sure you want to exit', icon='warning')
    if mbox == 'yes':
        root.destroy()


menuBar = Menu(root)
root.config(menu=menuBar)
file = Menu(menuBar, tearoff=0)
menuBar.add_cascade(label='File', menu=file)
file.add_command(label='New')
file.add_separator()
file.add_command(label='Open')
file.add_command(label='Save')
# icon = PhotoImage(file='icons/exit.png')
file.add_command(label='Exit', compound=LEFT, command=funcExit)
edit = Menu(menuBar)
about = Menu(menuBar)



root.geometry('650x650+350+250')
root.mainloop()
from tkinter import *
from tkinter import ttk

root = Tk()


def callback():
    val1 = entry.get()
    val2 = entry2.get()
    print("Your name is: " + val1)
    print("Your Password is: " + val2)


entry = ttk.Entry(root, width=30)
entry2 = ttk.Entry(root, width=30)
entry.insert(0, "Please enter your name")
entry2.config(show='*')
button = ttk.Button(root, text="Click Me!", command=callback)
entry.pack()
entry2.pack()
button.pack()
root.geometry("300x300")
entry.state(['disabled'])
entry.state(['!disabled'])
entry.state(['readonly'])
root.mainloop()

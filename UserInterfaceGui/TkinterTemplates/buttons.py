from tkinter import *
from tkinter import ttk

root = Tk()


def callback():
    label.config(text='You clicked me!', fg='red', bg='yellow')


label = Label(root, text="Hello Python")
label.pack()
button = Button(root, text='Click ME!', command=callback)
button['state'] = 'disabled'
button['state'] = 'normal'

button.pack()
root.geometry("350x300")
root.mainloop()
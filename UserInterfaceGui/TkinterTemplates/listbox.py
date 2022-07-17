from tkinter import *
from tkinter import ttk

root = Tk()


def print_me():
    selected_item = listBox.curselection()
    for item in selected_item:
        print(listBox.get(item))


def delete_me():
    selected_item = listBox.curselection()
    for item in selected_item:
        listBox.delete(item)


listBox = Listbox(root, width=40, height=15, selectmode=MULTIPLE)
listBox.insert(0, "Python")
listBox.insert(1, "C++")
listBox.insert(2, "C#")
listBox.insert(3, "PHP")
listBox.pack(pady=25)

button = Button(root, text='Print', command=print_me)
button.place(x=300, y=300)

button2 = Button(root, text='Delete', command=delete_me)
button2.place(x=350, y=300)

root.geometry('650x650+650+200')
root.mainloop()
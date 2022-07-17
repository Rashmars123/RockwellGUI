from tkinter import *
from tkinter import ttk

root = Tk()

# icon = PhotoImage(file='icons/icon_tab.png')
tabs = ttk.Notebook(root)
tabs.pack(fill=BOTH, expand=True)

tab1 = ttk.Frame(tabs)
tab2 = ttk.Frame(tabs)

tabs.add(tab1, text='First Tab')
# tabs.add(tab2, text='Second Tab', image=icon, compound=LEFT)
tabs.add(tab2, text='Second Tab')
lbl = ttk.Label(tab1, text='Hello')
lbl.place(x=200, y=20)

button = ttk.Button(tab2, text='Click ME!')
button.place(x=250, y=50)
root.geometry('550x550+650+200')
root.mainloop()

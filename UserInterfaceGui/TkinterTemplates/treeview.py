from tkinter import *
from tkinter import ttk

root = Tk()


def callback(event):
    item = treeview.identify('item', event.x, event.y)
    print(f'You clicked on {treeview.item(item, "text")} ')


treeview = ttk.Treeview(root)
treeview.pack()
icon = PhotoImage(file='icons/exit.png')
treeview.insert('', 0, 'item1', text='First Item', image=icon)
treeview.insert('', 1, 'item2', text='Second Item')
treeview.insert('', 2, 'item3', text='Third Item')
treeview.insert('', 3, 'item4', text='Four Item')
treeview.move('item3', 'item1', 'end')
treeview.bind('<Double-1>', callback)
root.geometry("650x650+350+250")
root.mainloop()

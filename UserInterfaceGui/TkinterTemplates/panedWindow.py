from tkinter import *
from tkinter import ttk

root = Tk()

pw = ttk.Panedwindow(root, orient=HORIZONTAL)
pw.pack(fill=BOTH, expand=True)

frame = ttk.Frame(pw, width=100, height=500, relief=SUNKEN)
frame2 = ttk.Frame(pw, width=300, height=500, relief=SUNKEN)
frame3 = ttk.Frame(pw, width=75, height=500, relief=SUNKEN)

pw.add(frame, weight=1)
pw.add(frame2, weight=3)
pw.insert(pos=1, child=frame3)

lbl = Label(frame, text='Hello')
lbl.grid(row=0, column=0, pady=25)
button = ttk.Button(frame, text='Click Me')
button.grid(row=1, column=0, padx=20, pady=25)

root.geometry('550x550+300+50')
root.mainloop()
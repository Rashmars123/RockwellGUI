from tkinter import *
from tkinter import ttk

root = Tk()

# Progress Bar

progbar = ttk.Progressbar(root, orient=HORIZONTAL, length=200)
progbar.pack(pady=20)
progbar.config(mode='indeterminate')
progbar.start()
progbar.stop()
progbar.config(mode='determinate', maximum=50.0, value=10)
progbar.start()
progbar.stop()

value=DoubleVar()
scale = ttk.Scale(root, orient=HORIZONTAL, length=200, variable=value, from_=0.0, to=50.0)
scale.pack()

progbar.config(variable=value)

root.geometry("450x450+650+350")
root.mainloop()
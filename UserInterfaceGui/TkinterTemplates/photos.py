from tkinter import *

root = Tk()

lbl_text = Label(root, text='Using Images', font=(('Times'), 18))
lbl_text.pack()

logo = PhotoImage(file='icons/icon.png')
lbl_image = Label(root, image=logo)
lbl_image.pack()

root.geometry('350x350')
root.mainloop()
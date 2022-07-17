from tkinter import *

root = Tk()
label = Label(root, text='Hello Python')
# label['text'] = "Hello Tkinter"
label.config(text="Hello Tkinter", fg='red')
label.config(bg='yellow')
label.config(font="Times 15")
label.config(text='Hello Python I love you so much!')
label.config(wraplength="150")  # 150 pixels
label.config(justify=RIGHT)
label.pack()
root.geometry("300x250")
root.mainloop()
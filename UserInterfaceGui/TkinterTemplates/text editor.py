from tkinter import *

root = Tk()


def callback():
    result = textEditor.get(1.0, END)
    print(result)


textEditor = Text(root, width=30, height=10, font=('Times', 15), wrap=WORD)
textEditor.grid(row=0, column=0, pady=20, padx=40)
textEditor.insert(INSERT, "Hello I am a tkinter widget")
textEditor.config(state='disabled')
textEditor.config(state='normal')
button = Button(root, text='Save', width=10, height=1, command=callback)
button.grid(row=3, column=0)
root.geometry("550x550")
root.mainloop()
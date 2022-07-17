from tkinter import *
root = Tk()
root.title("Frames")

frame = Frame(root, height=300, width=300, bg='red', bd='7', relief=SUNKEN)
frame.pack(fill=X)
button1 = Button(frame, text='Button1')
button2 = Button(frame, text='Button2')
button1.pack(side=LEFT, padx=20, pady=50)
button2.pack(side=RIGHT, padx=20, pady=50)

searchBar = LabelFrame(root, text='Search Box')
lbl = Label(searchBar, text="Search")
lbl.pack(side=LEFT, padx=10)
searchBar.pack(side=TOP)
entry = Entry(searchBar)
entry.pack(side=LEFT, padx=10)
button = Button(searchBar, text="Search")
button.pack(side=LEFT, padx=10, pady=10)

root.geometry("650x650+450+200")
root.mainloop()
from tkinter import *
from tkinter import ttk

root = Tk()


def callback():
    print(f"Your Name: {entry.get()}")
    print(f"Your Password: {entry2.get()}")
    if chvar.get() == 1:
        print("Remember me selected")
    else:
        print("Not selected")
    print(f'Your Gender is: {gender.get()}')
    print(f'The month is: {months.get()}')
    print(f'The year is: {year.get()}')


# Label
lbltitle = ttk.Label(text='Our Title Here', font=('Arial', 22))
lblname = ttk.Label(text="Your Name: ", justify=CENTER)
lblpass = ttk.Label(text="Your Password: ", justify=CENTER)

lbltitle.grid(row=0, column=0, columnspan=2)
lblname.grid(row=1, column=0, )
lblpass.grid(row=2, column=0, )

# Entry
entry = ttk.Entry(root, width=30)
entry2 = ttk.Entry(root, width=30)
entry.insert(0, 'Please enter your name')
entry2.insert(0, 'Please enter your password')
entry.grid(row=1, column=1)
entry2.grid(row=2, column=1)

# Button
button = ttk.Button(root, text='Enter')
button.grid(row=3, column=1, sticky=E+W, pady=5)
button.config(command=callback)

# Checkbox
chvar = IntVar()
chvar.set(0)
cbox = Checkbutton(root, text='Remember me', variable=chvar, font='Arial 16')
cbox.grid(row=4, column=0, sticky=E, columnspan=2)
# Radio Buttons
gender = StringVar()

ttk.Radiobutton(root, text='male', value='male', variable=gender).grid(row=5, column=0)
ttk.Radiobutton(root, text='female', value='female', variable=gender).grid(row=5, column=1)

# Combo Box
months = StringVar()
numbers = []
for i in range(0, 10):
    numbers.append(str(i))
comboBox = ttk.Combobox(root,
                        textvariable=months,
                        values=numbers,
                        state='readonly')
comboBox.grid(row=6, column=0)

# Spinbox
year = StringVar()
Spinbox(root, from_=1990, to=2022, textvariable=year, state='readonly').grid(row=6, column=1)


root.geometry("500x450")
root.mainloop()
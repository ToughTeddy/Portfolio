from bst import BinaryTree
import buttons as b
from tkinter import *


tree = BinaryTree()
tree.treeify()

window = Tk()
window.title("Password Manager")
window.config(padx=50, pady=50)

photo = PhotoImage(file="logo.png")

canvas = Canvas(width=200, height=200, highlightthickness=0)
canvas.create_image(120, 120, image=photo)
canvas.grid(column=1, row=0, pady=20)

website = Label(text="Website:")
website.grid(column=0, row=1)

website_entry = Entry(width=32)
website_entry.focus()
website_entry.grid(column=1, row=1, sticky=E)

web_search = Button(width=14, text="Search", command=lambda: b.info_search(tree, website_entry))
web_search.grid(column=2, row=1)

email = Label(text="Email/Username:")
email.grid(column=0, row=2)

email_entry = Entry(width=49)
email_entry.insert(0, "kstoeck99@outlook.com")
email_entry.grid(column=1, row=2, columnspan=2)

password = Label(text="Password:")
password.grid(column=0, row=3)

password_entry = Entry(width=32)
password_entry.grid(column=1, row=3, sticky=E)

generator = Button(width=14, text="Generate Password", command=lambda: b.generate_pw(password_entry))
generator.grid(column=2, row=3)

add = Button(width=41, text="Add", command=lambda: b.save(tree, website_entry, email_entry, password_entry))
add.grid(column=1, row=4, columnspan=2)


window.mainloop()
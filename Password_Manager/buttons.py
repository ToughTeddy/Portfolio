from random import choice, randint, shuffle
import pyperclip
from tkinter import messagebox, END

letters = ['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u',
           'v','w','x','y','z','A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P',
           'Q','R','S','T','U','V','W','X','Y','Z']
numbers = ['0','1','2','3','4','5','6','7','8','9']
symbols = ['!','#','$','%','&','(',')','*','+']

def generate_pw(password_entry):
    password_entry.delete(0, END)

    nr_letters = randint(8, 10)
    nr_upper_letters = randint(2, 4)

    upper_letters_l = [choice(letters).upper() for _ in range(nr_upper_letters)]
    lower_letters_l = [choice(letters) for _ in range(nr_letters - nr_upper_letters)]
    symbols_l = [choice(symbols) for _ in range(randint(2, 4))]
    numbers_l = [choice(numbers) for _ in range(randint(2, 4))]

    password_list = upper_letters_l + lower_letters_l + symbols_l + numbers_l
    shuffle(password_list)
    new_password = "".join(password_list)

    password_entry.insert(0, new_password)
    pyperclip.copy(new_password)

def info_search(tree, website_entry):
    site = website_entry.get().strip()
    if not site:
        messagebox.showerror("Error", "Please enter website name.")
        return

    result = tree.search_tree(site)
    if result is None:
        messagebox.showerror("Error", "Website not found.")
    else:
        address = result["email"]
        pw = result["password"]
        messagebox.showinfo(site, f"Email: {address}\nPassword: {pw}")

def save(tree, website_entry, email_entry, password_entry):
    web = website_entry.get().strip()
    address = email_entry.get().strip()
    pw = password_entry.get().strip()

    if not web or not address or not pw:
        messagebox.showinfo(title="Missing Info", message="Please check your entries for missing info!")
        return

    existing = tree.search_tree(web)
    if existing:
        messagebox.showerror("Error", "That website already exists.")
        return

    ok = messagebox.askokcancel(title=web, message=f"Is the information correct?\nEmail: {address}\nPassword: {pw}")
    if ok:
        try:
            tree.add(web, pw, address)
            website_entry.delete(0, END)
            password_entry.delete(0, END)
        except Exception as e:
            messagebox.showerror("Error", f"Could not save data.\n{str(e)}")

from tkinter import *


window = Tk()
window.title("ISS Tracker")
window.config(padx=50, pady=50)

canvas = Canvas(width=300, height=414)

start_function = Button(text="Start Checking", highlightthickness=0)
start_function.grid(row=0, column=0)

darkness = Label(text="Night Time: Press Start")
darkness.grid(row=1, column=0)

nearness = Label(text="ISS Near Location: Press Start")
nearness.grid(row=2, column=0)

email = Label(text="Email Sent: Press Start")
email.grid(row=3, column=0)

window.mainloop()
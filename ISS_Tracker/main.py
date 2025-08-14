from tkinter import *
import sun_tracker as sun
import iss_tracker as iss
import email_util as em

timer = None

def main():
    global timer
    start_function["text"] = "Running..."
    if timer:
        window.after_cancel(timer)
    close = iss.iss_close_check()
    dark = sun.dark_check()

    if dark:
        darkness["text"] = "Night Time: Yes"
    else:
        darkness["text"] = "Night Time: No"
    if close:
        nearness["text"] = "ISS Near Location: Yes"
    else:
        nearness["text"] = "ISS Near Location: No"
    if close and dark:
        email["text"] = "Email Sent: Yes"
        em.look_up()
    else:
        email["text"] = "Email Sent: No"
    print("ISS Checked")
    timer = window.after(60000, func=main)

window = Tk()
window.title("ISS Tracker")
window.config(padx=50, pady=50)

canvas = Canvas(width=300, height=414)

start_function = Button(text="Start Checking", highlightthickness=0, command=main)
start_function.grid(row=0, column=0)

darkness = Label(text="Night Time: Press Start")
darkness.grid(row=1, column=0)

nearness = Label(text="ISS Near Location: Press Start")
nearness.grid(row=2, column=0)

email = Label(text="Email Sent: Press Start")
email.grid(row=3, column=0)

window.mainloop()
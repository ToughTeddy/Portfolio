import os, json
from pathlib import Path


# load local.settings.json variables
def _load_env():
    here = Path(__file__).resolve()
    for d in (here.parent, *here.parents):
        f = d / "local.settings.json"
        if f.exists():
            try:
                vals = json.load(open(f, "r", encoding="utf-8")).get("Values", {})
                for k, v in vals.items():
                    os.environ.setdefault(k, str(v))
            except Exception:
                pass
            break
_load_env()


from tkinter import *
import sun_tracker as sun
import iss_tracker as iss
import email_util as em


timer_id = None

def schedule_next():
    """set timer to 60 seconds"""
    global timer_id
    timer_id = window.after(60_000, run_once)

def stop_loop():
    """stop timer loop"""
    global timer_id
    if timer_id:
        window.after_cancel(timer_id)
        timer_id = None
    start_button["text"] = "Start"

def run_once():
    """main app loop"""
    global timer_id
    start_button["text"] = "Running…"
    if timer_id:
        window.after_cancel(timer_id)
        timer_id = None

    try:
        dark = sun.dark_check()
        close = iss.iss_close_check()
    except Exception as e:
        darkness["text"] = "Night Time: (error)"
        nearness["text"] = "ISS Near Location: (error)"
        email_status["text"] = "Email Sent: (skipped)"
        print(f"Check failed: {e}")
        schedule_next()
        return

    darkness["text"] = f"Night Time: {'Yes' if dark else 'No'}"
    nearness["text"] = f"ISS Near Location: {'Yes' if close else 'No'}"

    if dark and close:
        try:
            em.look_up()
            email_status["text"] = "Email Sent: Yes"
        except Exception as e:
            email_status["text"] = "Email Sent: Error"
            print(f"Email failed: {e}")
    else:
        email_status["text"] = "Email Sent: No"

    print("ISS Checked")
    schedule_next()

def start_loop():
    run_once()


window = Tk()
window.title("ISS Tracker")
window.config(padx=50, pady=50)

start_button = Button(text="Start", highlightthickness=0, command=start_loop)
start_button.grid(row=0, column=0)

stop_button = Button(text="Stop", highlightthickness=0, command=stop_loop)
stop_button.grid(row=0, column=1)

darkness = Label(text="Night Time: Press Start")
darkness.grid(row=1, column=0, columnspan=2, sticky="w")

nearness = Label(text="ISS Near Location: Press Start")
nearness.grid(row=2, column=0, columnspan=2, sticky="w")

email_status = Label(text="Email Sent: Press Start")
email_status.grid(row=3, column=0, columnspan=2, sticky="w")

window.mainloop()

import logging
import azure.functions as func

import sun_tracker as sun
import iss_tracker as iss
import email_util as em

app = func.FunctionApp()


@app.function_name(name="iss_tracker")
@app.schedule(schedule="0 */5 * * * *", arg_name="mytimer", run_on_startup=False, use_monitor=True)
def iss_tracker_timer(mytimer: func.TimerRequest) -> None:
    try:
        if mytimer and mytimer.past_due:
            logging.warning("⏰ Timer is running late.")

        # Only run at night
        if not sun.dark_check():
            logging.info("☀️ Daylight — skipping this run.")
            return

        # Run the proximity check; send email if close
        if iss.iss_close_check():
            logging.info("🛰️ ISS is close & it's dark — sending email.")
            em.look_up()
        else:
            logging.info("🛰️ ISS not within range right now.")

    except Exception as e:
        logging.exception("🚨 iss_tracker run failed: %s", e)
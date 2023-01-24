# sleep_if.py
import datetime
import time


def sleep_if(morning=9, evening=17):
    time_string = str(evening) + 'am' if evening < 13 else str(evening - 12) + 'pm'
    today = datetime.datetime.now()
    midnight = today.replace(hour=0, minute=0, second=0, microsecond=0)
    seconds_since_midnight = (today - midnight).seconds
    if morning * 60 * 60 < seconds_since_midnight & seconds_since_midnight < evening * 60 * 60:
        print(f'sleeping til {time_string} tonight')
        time.sleep(evening * 60 * 60 - seconds_since_midnight)

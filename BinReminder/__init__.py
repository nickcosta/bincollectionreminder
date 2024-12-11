import datetime
import azure.functions as func
from twilio.rest import Client
import os

# Twilio credentials
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
phone_numbers = os.environ["PHONE_NUMBERS"].split(";")

# Bin pattern in the exact sequence required
bin_pattern = ["black", "blue", "black", "brown"]

# Environment variable that will store the current index
CURRENT_INDEX_VAR = "CURRENT_INDEX"

def get_current_index():
    val = os.environ.get(CURRENT_INDEX_VAR, "")
    if val.isdigit():
        idx = int(val)
        return idx % len(bin_pattern)
    # Default to 0 (black) if not set or invalid
    return 0

def set_current_index(idx):
    # This will NOT persist in Azure after the function finishes!
    # It only updates the in-memory environment for the current execution.
    os.environ[CURRENT_INDEX_VAR] = str(idx)

def send_sms(message, numbers):
    client = Client(account_sid, auth_token)
    for number in numbers:
        try:
            msg = client.messages.create(
                to=number, from_=twilio_phone_number, body=message
            )
            print(f"SMS Sent to: {number}, SID: {msg.sid}")
        except Exception as e:
            print(f"Failed to send SMS to {number}: {e}")
    print("SMS Sent to:", numbers)

def main(mytimer: func.TimerRequest):
    current_index = get_current_index()
    # Move to the next index in the cycle
    next_index = (current_index + 1) % len(bin_pattern)
    next_color = bin_pattern[next_index]

    # Update the "env variable" for the current run
    set_current_index(next_index)

    # Prepare the reminder message
    next_day = datetime.date.today() + datetime.timedelta(days=1)
    message = f"Reminder: Put out the {next_color} bin now for tomorrow ({next_day.strftime('%Y-%m-%d')})."
    send_sms(message, phone_numbers)

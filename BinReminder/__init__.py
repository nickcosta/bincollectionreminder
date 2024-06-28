import datetime
import azure.functions as func
from twilio.rest import Client
import os

# Twilio credentials
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
phone_numbers = os.environ["PHONE_NUMBERS"].split(";")

# Define the bin color pattern
bin_pattern = ["blue", "black", "brown", "black"]

# Environment variable to store the previous bin color
PREVIOUS_BIN_COLOR = "PREVIOUS_BIN_COLOR"

def send_sms(message, numbers):
    """
    Send an SMS to a list of phone numbers.
    """
    client = Client(account_sid, auth_token)
    for number in numbers:
        try:
            message = client.messages.create(
                to=number, from_=twilio_phone_number, body=message
            )
            print(f"SMS Sent to: {number}, SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS to {number}: {e}")
    print("SMS Sent to:", numbers)

def get_previous_bin_color():
    """
    Get the previous bin color from the environment variable.
    """
    return os.environ.get(PREVIOUS_BIN_COLOR, "black")

def set_previous_bin_color(color):
    """
    Set the previous bin color to the environment variable.
    """
    os.environ[PREVIOUS_BIN_COLOR] = color

def get_next_bin_color(previous_color):
    """
    Get the next bin color based on the previous bin color.
    """
    if previous_color == "blue":
        return "black"
    elif previous_color == "black":
        next_index = (bin_pattern.index(previous_color, bin_pattern.index(previous_color) + 1) % len(bin_pattern)) + 1
        return bin_pattern[next_index % len(bin_pattern)]
    elif previous_color == "brown":
        return "black"
    else:
        return "blue"  # default to blue if previous_color is not in the expected values

def main(mytimer: func.TimerRequest):
    next_day = datetime.date.today() + datetime.timedelta(days=1)

    previous_color = get_previous_bin_color()
    next_color = get_next_bin_color(previous_color)
    set_previous_bin_color(next_color)

    message = f"Reminder: Put out the {next_color} bin now for tomorrow ({next_day.strftime('%Y-%m-%d')})."
    send_sms(message, phone_numbers)

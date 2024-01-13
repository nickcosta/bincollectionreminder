import datetime
import azure.functions as func
from twilio.rest import Client
import os

# Twilio credentials
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
phone_numbers = os.environ["PHONE_NUMBERS"].split(";")

# Sample bin schedule
bin_schedule = {
    2024: {
        "January": {
            2: "test",
            3: "brown",
            10: "black",
            14: "black",
            17: "blue",
            24: "black",
            31: "brown",
        },
        "February": {7: "black", 14: "blue", 21: "black", 28: "brown"},
        "March": {6: "black", 13: "blue", 20: "black", 27: "brown"},
        "April": {3: "black", 10: "blue", 17: "black", 24: "brown"},
        "May": {1: "black", 8: "blue", 15: "black", 22: "brown", 29: "black"},
        "June": {5: "blue", 12: "black", 19: "brown", 26: "black"},
        # Add other months and dates as necessary
    },
    # Add other years as necessary
}


def send_sms(message, numbers):
    """
    Send an SMS to a list of phone numbers.
    """
    client = Client(account_sid, auth_token)
    for number in numbers:
                try:
            message = client.messages.create(
                to=number, 
                from_=twilio_phone_number, 
                body=message
            )
            print(f"SMS Sent to: {number}, SID: {message.sid}")
        except Exception as e:
            print(f"Failed to send SMS to {number}: {e}")
        print("SMS Sent to:", numbers)


def check_and_send_sms():
    today = datetime.date.today()
    next_day = today + datetime.timedelta(days=1)
    year = next_day.year
    month = next_day.strftime("%B")
    day = next_day.day

    if year in bin_schedule:
        if month in bin_schedule[year]:
            if day in bin_schedule[year][month]:
                bin_color = bin_schedule[year][month][day]
                message = f"Reminder: Put out the {bin_color} bin now for tomorrow ({next_day.strftime('%Y-%m-%d')})."
                send_sms(message, phone_numbers)


if __name__ == "__main__":
    check_and_send_sms()

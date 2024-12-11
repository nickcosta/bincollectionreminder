import datetime
import azure.functions as func
from twilio.rest import Client
import os
from azure.storage.blob import BlobServiceClient

# Twilio credentials
account_sid = os.environ["TWILIO_ACCOUNT_SID"]
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
twilio_phone_number = os.environ["TWILIO_PHONE_NUMBER"]
phone_numbers = os.environ["PHONE_NUMBERS"].split(";")

bin_pattern = ["black", "blue", "black", "brown"]

# Use the environment variable that points to your blob connection string
connection_str = os.environ["BLOB_CONNECTION_STRING"]
container_name = "state"
blob_name = "current_index.txt"

def get_current_index():
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_str)
    container_client = blob_service_client.get_container_client(container_name)
    try:
        container_client.create_container()
    except:
        pass

    blob_client = container_client.get_blob_client(blob_name)

    if not blob_client.exists():
        return 0

    data = blob_client.download_blob().readall().decode("utf-8").strip()
    if data.isdigit():
        idx = int(data)
        return idx % len(bin_pattern)
    return 0

def set_current_index(idx):
    blob_service_client = BlobServiceClient.from_connection_string(conn_str=connection_str)
    container_client = blob_service_client.get_container_client(container_name)
    blob_client = container_client.get_blob_client(blob_name)
    blob_client.upload_blob(str(idx), overwrite=True)

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
    next_index = (current_index + 1) % len(bin_pattern)
    next_color = bin_pattern[next_index]

    set_current_index(next_index)

    next_day = datetime.date.today() + datetime.timedelta(days=1)
    message = f"Reminder: Put out the {next_color} bin now for tomorrow ({next_day.strftime('%Y-%m-%d')})."
    send_sms(message, phone_numbers)

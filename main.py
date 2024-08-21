import os
import datetime
import pickle
import pandas as pd
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# If modifying these SCOPES, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

def authenticate_google():
    creds = None
    # The file token.pickle stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def get_calendar_service():
    creds = authenticate_google()
    service = build('calendar', 'v3', credentials=creds)
    return service

def get_free_busy(service, calendars, time_min, time_max):
    body = {
        "timeMin": time_min,
        "timeMax": time_max,
        "items": [{"id": calendar_id} for calendar_id in calendars]
    }
    freebusy_result = service.freebusy().query(body=body).execute()
    return freebusy_result.get('calendars', {})

def find_common_free_slots(free_busy_data, time_min, time_max):
    busy_slots = []
    for calendar_id, info in free_busy_data.items():
        busy_slots.extend(info['busy'])

    # Convert to DataFrame
    df = pd.DataFrame(busy_slots)
    df['start'] = pd.to_datetime(df['start'])
    df['end'] = pd.to_datetime(df['end'])

    # Create a series of time ranges (all possible 30-minute intervals)
    time_range = pd.date_range(start=time_min, end=time_max, freq='30T')

    # Check which time slots are free by comparing against busy intervals
    free_slots = []
    for start_time in time_range:
        end_time = start_time + pd.Timedelta(minutes=30)
        if not any((df['start'] < end_time) & (df['end'] > start_time)):
            free_slots.append((start_time, end_time))

    return free_slots

def main():
    service = get_calendar_service()

    # Replace these with the emails of the users' calendars you want to check
    calendar_ids = [
        'user1@example.com',
        'user2@example.com',
        'user3@example.com'
    ]

    # Define the time range for checking availability
    time_min = datetime.datetime.utcnow().isoformat() + 'Z'
    time_max = (datetime.datetime.utcnow() + datetime.timedelta(days=7)).isoformat() + 'Z'

    # Get free/busy information
    free_busy_data = get_free_busy(service, calendar_ids, time_min, time_max)

    # Find common free time slots
    common_free_slots = find_common_free_slots(free_busy_data, time_min, time_max)

    # Print common free slots
    print("Common Free Time Slots:")
    for start, end in common_free_slots:
        print(f"Start: {start}, End: {end}")

if __name__ == '__main__':
    main()

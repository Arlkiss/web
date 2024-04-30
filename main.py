from flask import Flask, request, jsonify
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import datetime


# файлы с учетными данными для Google API
CLIENT_SECRETS_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly', 'https://www.googleapis.com/auth/calendar']


app = Flask(__name__)


def get_calendar_service():
    flow = InstalledAppFlow.from_client_secrets_file(
        'client_secret.json', SCOPES,
        redirect_uri='http://localhost:8080')
    credentials = flow.run_local_server()
    service = build('calendar', 'v3', credentials=credentials)
    return service


@app.route('/schedule', methods=['GET'])
def get_schedule():
    # логика для получения расписания из Google Calendar
    service = get_calendar_service()
    now = datetime.datetime.utcnow().isoformat() + 'Z'
    events_result = service.events().list(calendarId='primary', timeMin=now,
                                          maxResults=10, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    return jsonify(events)
    

@app.route('/event', methods=['POST'])
def create_event():
    # логика для создания события в Google Calendar
    service = get_calendar_service()
    event = request.get_json()
    event = service.events().insert(calendarId='primary', body=event).execute()
    return jsonify(event)


@app.route('/event', methods=['DELETE'])
def delete_event():
    # логика для удаления события из Google Calendar
    service = get_calendar_service()
    event_id = request.args.get('event_id')
    service.events().delete(calendarId='primary', eventId=event_id).execute()
    return jsonify({'message': 'Event deleted'})


@app.route('/reminder', methods=['POST'])
def create_reminder(event_id=None):
    # логика для создания напоминания в Google Calendar
    service = get_calendar_service()
    reminder = {
        'minutes': minutes,
        'method': 'popup'
    }
    service.events().get(eventId=event_id).execute()
    service.events().update(eventId=event_id, body={'reminders': {'overrides': [reminder]}},
                            sendNotifications=True).execute()

@app.route('/reminder', methods=['DELETE'])
def delete_reminder():
    # логика для удаления напоминания из Google Calendar
    service = get_calendar_service()
    event_id = request.args.get('event_id')
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return jsonify({'message': 'Reminder deleted successfully'})
    except HttpError as e:
        return jsonify({'error': 'An error occurred while deleting the reminder', 'details': str(e)})


def main():
    flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRETS_FILE, SCOPES)
    credentials = flow.run_console()
    credentials.refresh(Request())

    service = build('calendar', 'v3', credentials=credentials)

    app.run()

if __name__ == '__main__':
    main()
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import re

class GoogleSheetsHelper:
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive']
    SERVICE_ACCOUNT_FILE = 'C:/Users/Razer/Documents/42R/powerfulapp.json'

    def __init__(self):
        creds = Credentials.from_service_account_file(
            self.SERVICE_ACCOUNT_FILE, scopes=self.SCOPES)
        self.service = build('sheets', 'v4', credentials=creds)
        self.drive_service = build('drive', 'v3', credentials=creds)

    def create_sheet_and_share(self, title, emails, role='reader'):
        spreadsheet = self.service.spreadsheets().create(body={
            'properties': {'title': title}
        }).execute()
        spreadsheet_id = spreadsheet.get('spreadsheetId')
        
        for email in emails:
            self.drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={'type': 'user', 'role': role, 'emailAddress': email},
                fields='id'
            ).execute()
        
        return f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"

    # def add_data_to_sheet(self, spreadsheet_id, range_name, values):
    #     body = {
    #         'values': values
    #     }
    #     result = self.service.spreadsheets().values().update(
    #         spreadsheetId=spreadsheet_id, range=range_name,
    #         valueInputOption='RAW', body=body).execute()
    #     return result

    def read_data_from_sheet(self, spreadsheet_id, range_name):
        result = self.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id, range=range_name).execute()
        return result.get('values', [])

    def add_data_to_sheet(self, spreadsheet_id, range_name, values):
        body = {
            'values': values
        }
        result = self.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption='USER_ENTERED', insertDataOption='INSERT_ROWS', body=body).execute()
        return result

    # def read_data_from_sheet(self, spreadsheet_id, sheet_name='Sheet1'):
    #     # Using a broad range to capture all potential data.
    #     range_name = f'{sheet_name}!A1:Z1000'  # Adjust the column range and row range as needed
    #     result = self.service.spreadsheets().values().get(
    #         spreadsheetId=spreadsheet_id, range=range_name).execute()
    #     return result.get('values', [])

    def share_sheet(self, spreadsheet_id, email_addresses, role='reader', notify=True, email_message='Here is the Google Sheet I shared with you.'):
        """
        Share a Google Sheet with specified users.

        Parameters:
        - spreadsheet_id: The ID of the spreadsheet to share.
        - email_addresses: A list of email addresses to share the sheet with.
        - role: The role to grant. Options include 'owner', 'writer', and 'reader'.
        - notify: Whether to send email notifications to the new users (True/False).
        - email_message: The custom message to include in the notification email.
        """
        for email in email_addresses:
            self.drive_service.permissions().create(
                fileId=spreadsheet_id,
                body={
                    'type': 'user',
                    'role': role,
                    'emailAddress': email
                },
                fields='id',
                sendNotificationEmail=notify,
                emailMessage=email_message
            ).execute()


    def extract_spreadsheet_id_from_url(self, sheet_url):
        """
        Extracts the spreadsheet ID from a Google Sheet URL.

        Parameters:
        - sheet_url: The full URL of the Google Sheet.

        Returns:
        The extracted spreadsheet ID or None if the URL is invalid.
        """
        match = re.search(r"/spreadsheets/d/([a-zA-Z0-9-_]+)", sheet_url)
        if match:
            return match.group(1)
        return None
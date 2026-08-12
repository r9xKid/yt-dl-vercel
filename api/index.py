import os
import json
from io import BytesIO
from http.server import BaseHTTPRequestHandler

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload


def get_drive_service():
    private_key = os.environ["GOOGLE_PRIVATE_KEY"].replace("\\n", "\n")

    credentials_info = {
        "type": "service_account",
        "client_email": os.environ["GOOGLE_SERVICE_ACCOUNT_EMAIL"],
        "private_key": private_key,
        "token_uri": "https://oauth2.googleapis.com/token",
    }

    credentials = service_account.Credentials.from_service_account_info(
        credentials_info,
        scopes=["https://www.googleapis.com/auth/drive"],
    )

    return build("drive", "v3", credentials=credentials)


class handler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            drive = get_drive_service()

            folder_id = os.environ["GOOGLE_DRIVE_FOLDER_ID"]

            test_file = BytesIO(
                b"Vercel Google Drive connection test"
            )

            metadata = {
                "name": "vercel-test.txt",
                "parents": [folder_id],
            }

            media = MediaIoBaseUpload(
                test_file,
                mimetype="text/plain",
                resumable=False,
            )

            created = drive.files().create(
                body=metadata,
                media_body=media,
                fields="id,name",
            ).execute()

            file_id = created["id"]

            drive.files().delete(
                fileId=file_id
            ).execute()

            response = {
                "success": True,
                "message": "Google Drive connection works!",
                "file_created_and_deleted": True
            }

            self.send_response(200)

        except Exception as e:

            response = {
                "success": False,
                "error": str(e)
            }

            self.send_response(500)

        self.send_header(
            "Content-Type",
            "application/json"
        )

        self.end_headers()

        self.wfile.write(
            json.dumps(response).encode("utf-8")
        )

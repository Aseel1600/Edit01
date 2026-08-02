#!/usr/bin/env python3
"""
OpenMontage - Official YouTube Data API v3 Direct Uploader
Uploads rendered videos (.mp4) directly to YouTube using Google API Client.
"""

import sys
import os
import json
import argparse
import subprocess
import time

try:
    import googleapiclient.discovery
    import googleapiclient.errors
    from googleapiclient.http import MediaFileUpload
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.oauth2.credentials import Credentials
    from google.auth.transport.requests import Request
    HAS_GOOGLE_API = True
except ImportError:
    HAS_GOOGLE_API = False

SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

def get_authenticated_service(client_secrets_file="client_secrets.json", token_file="token.json"):
    creds = None
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)
        
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not os.path.exists(client_secrets_file):
                raise FileNotFoundError(f"Missing OAuth2 secrets file: {client_secrets_file}. Download it from Google Cloud Console.")
            flow = InstalledAppFlow.from_client_secrets_file(client_secrets_file, SCOPES)
            creds = flow.run_local_server(port=0)
            
        with open(token_file, "w") as token:
            token.write(creds.to_json())
            
    return googleapiclient.discovery.build("youtube", "v3", credentials=creds)

def upload_video_api(video_path, title, description="", category_id="27", tags=None, privacy_status="unlisted"):
    if not HAS_GOOGLE_API:
        raise ImportError("google-api-python-client is not installed.")

    print(f"[YouTube API v3] Initializing direct upload for: {video_path}")
    youtube = get_authenticated_service()

    body = {
        "snippet": {
            "title": title,
            "description": description,
            "tags": tags or ["OpenMontage", "AI Video", "Documental", "Análisis"],
            "categoryId": category_id
        },
        "status": {
            "privacyStatus": privacy_status,
            "selfDeclaredMadeForKids": False
        }
    }

    media = MediaFileUpload(video_path, chunksize=-1, resumable=True, mimetype="video/mp4")
    request = youtube.videos().insert(part="snippet,status", body=body, media_body=media)

    print("[YouTube API v3] Uploading chunks...")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Uploaded {int(status.progress() * 100)}%")

    print(f"[YouTube API v3] Upload Complete! Video ID: {response['id']}")
    print(f"Watch URL: https://www.youtube.com/watch?v={response['id']}")
    return response

def main():
    parser = argparse.ArgumentParser(description="Official YouTube Data API v3 Uploader.")
    parser.add_argument("--video", required=True, help="Path to MP4 file")
    parser.add_argument("--title", required=True, help="Video title")
    parser.add_argument("--description", default="", help="Video description")
    parser.add_argument("--privacy", default="unlisted", choices=["public", "unlisted", "private"])
    parser.add_argument("--secrets", default="client_secrets.json", help="Path to Google Cloud client_secrets.json")
    
    args = parser.parse_args()
    
    try:
        res = upload_video_api(args.video, args.title, args.description, privacy_status=args.privacy)
        print(json.dumps(res, indent=2))
    except Exception as e:
        print(f"[API Setup Required] {e}")
        print("\nPara usar la API oficial de YouTube:")
        print("1. Crea un proyecto en Google Cloud Console (https://console.cloud.google.com).")
        print("2. Habilita 'YouTube Data API v3'.")
        print("3. Crea credenciales OAuth 2.0 y descarga 'client_secrets.json' en este directorio.")

if __name__ == "__main__":
    main()

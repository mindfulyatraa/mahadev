import os
import time
import random
import json
import sys
import requests # Added for Telegram
from datetime import datetime
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from googleapiclient.errors import HttpError

# OAuth2 Setup
SCOPES = ['https://www.googleapis.com/auth/youtube.force-ssl']

# VIRAL TITLES POOL (Generic & Catchy)
VIRAL_TITLES = [
    "You won't believe this! 😱 #shorts",
    "Wait for the end... 🔥 #shorts",
    "This 2D Animation is Next Level 🤣 #shorts",
    "Most Satisfying Animation Ever 🤤 #shorts",
    "OMG look at this detail! ✨ #shorts",
    "Did you see that? 🤯 #shorts",
    "Only 1% will get this 🧠 #shorts",
    "Best moment captured! 📸 #shorts",
    "Animation vs Reality 🎨 #shorts",
    "This is why I love 2D Animation ❤️ #shorts",
    "Legendary moment! 🏆 #shorts",
    "Too funny to handle 😂 #shorts",
    "Smooth animation check ✅ #shorts",
    "Respect the animator! 🫡 #shorts",
    "Mind blowing details 💥 #shorts"
]

def authenticate_youtube():
    """YouTube API Authentication (Headless Support)"""
    creds = None
    
    # 1. Check for Environment Variable (GitHub Actions / Headless)
    token_json_str = os.environ.get('YOUTUBE_TOKEN_JSON')
    
    if token_json_str:
        print("🤖 Headless Mode: Using Env Variable for Auth")
        try:
            token_info = json.loads(token_json_str)
            creds = Credentials.from_authorized_user_info(token_info, SCOPES)
        except Exception as e:
            print(f"❌ Error parsing YOUTUBE_TOKEN_JSON: {e}")
            
    # 2. Check for Local File
    elif os.path.exists('token.json'):
        print("💻 Local Mode: Using token.json")
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # 3. Refresh or Login (Only works locally with browser)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            print("🔄 Refreshing token...")
            creds.refresh(Request())
        else:
            if not os.path.exists('client_secrets.json'):
                print("❌ Error: No credentials found and client_secrets.json missing.")
                return None
            
            print("👤 Browser Login Required...")
            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)
        
        # Save token if running locally
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    return build('youtube', 'v3', credentials=creds)

def get_viral_metadata():
    """Returns a random viral title and standard description"""
    title = random.choice(VIRAL_TITLES)
    
    description = f"""{title}

👇 Subscribe for more daily doses of amazing animations! 
We upload the best 2D animations every day at 8 AM and 8 PM!

#shorts #viral #trending #funny #2danimation #animation #youtubeshorts #shortsfeed #satisfying #comedy"""

    tags = [
        "shorts", "viral", "trending", "funny", "tiktok", "reels", 
        "youtube shorts", "shorts feed", "algorithm", "2d animation", 
        "cartoon", "anime", "satisfying"
    ]
    
    return title, description, tags

def send_telegram_notification(video_title, video_id, channel_name="2D Animations"):
    """Sends a notification to Telegram"""
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    chat_id = os.environ.get('TELEGRAM_CHAT_ID')

    if not token or not chat_id:
        print("⚠️ Telegram secrets not found. Skipping notification.")
        return

    video_url = f"https://youtu.be/{video_id}"
    message = f"🚀 **New Video Uploaded!**\n\n📺 **Channel:** {channel_name}\n🎬 **Title:** {video_title}\n🔗 **Link:** {video_url}\n\n✅ Upload is Public & Live!"

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            print("📲 Telegram Notification Sent!")
        else:
            print(f"❌ Failed to send Telegram notification: {response.text}")
    except Exception as e:
        print(f"❌ Telegram Error: {e}")

def upload_and_delete_one_video(video_folder):
    """Uploads ONE video and deletes it (for GitHub Actions)"""
    
    # 1. Check Folder
    if not os.path.exists(video_folder):
        print(f"❌ Error: Video folder '{video_folder}' not found.")
        sys.exit(1)

    # 2. Find Videos
    video_files = [f for f in os.listdir(video_folder) 
                   if f.endswith(('.mp4', '.mov', '.avi', '.mkv'))]
    
    if not video_files:
        print("❌ No videos found to upload.")
        sys.exit(1)

    # 3. Pick Random Video
    video_file = random.choice(video_files)
    video_path = os.path.join(video_folder, video_file)
    print(f"\n🎬 Selected Video: {video_file}")

    # 4. Authenticate
    youtube = authenticate_youtube()
    if not youtube:
        print("❌ Authentication Failed.")
        sys.exit(1)

    # 5. Generate Metadata (Generic Viral)
    title, description, tags = get_viral_metadata()
    print(f"📝 Title: {title}")

    # 6. Upload (Public)
    body = {
        'snippet': {
            'title': title,
            'description': description,
            'tags': tags,
            'categoryId': '1' # Film & Animation
        },
        'status': {
            'privacyStatus': 'public', # DIRECT PUBLIC RELEASES
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(video_path, chunksize=-1, resumable=True)
    
    try:
        print("📤 Uploading...")
        request = youtube.videos().insert(
            part='snippet,status',
            body=body,
            media_body=media
        )
        
        response = None
        while response is None:
            status, response = request.next_chunk()
            if status:
                print(f"   ⏳ Progress: {int(status.progress() * 100)}%")
        
        video_id = response['id']
        print(f"✅ SUCCESS! Video ID: {video_id}")
        
        # 7. Delete File
        print("🗑️ Deleting uploaded file...")
        os.remove(video_path)
        print("✅ File processed and deleted.")

        # 8. Send Telegram Notification
        send_telegram_notification(title, video_id, channel_name="2D Animations")
        
    except HttpError as error:
        print(f"❌ Error: {error}")
        sys.exit(1)

if __name__ == "__main__":
    VIDEO_FOLDER = "videos"
    upload_and_delete_one_video(VIDEO_FOLDER)

# YouTube API Setup Guide

## 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project.
3. Enable **YouTube Data API v3**.
4. Go to **Credentials** -> **Create Credentials** -> **OAuth 2.0 Client ID**.
5. Select "Desktop App" as the application type.
6. Download the JSON file, rename it to `client_secrets.json`, and place it in this directory (`c:\Users\erson\Downloads\2d animations`).

## 2. Install Dependencies
Run the following command to install the required libraries:
```bash
pip install -r requirements.txt
```

## 3. Quota Limits
- Default Daily Quota: 10,000 units.
- Cost per upload: 1,600 units.
- Max uploads per day: ~6 videos.
- The script handles this by waiting 24 hours after every 6 videos.

## 4. Running the Script
1. Place your videos in the `videos` folder.
2. Run the script:
   ```bash
   python youtube_uploader.py
   ```
3. On the first run, a browser window will open for you to log in to your Google account. This will generate a `token.json` file for future runs.

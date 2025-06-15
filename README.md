# YouTube Playlist Downloader

This repository contains three Python scripts that work together to download members-only videos from YouTube playlists. The scripts handle both video and audio downloads, with features like automatic retries, progress tracking, and Windows notifications.

## Prerequisites

- Python 3.x
- Firefox browser (for cookies)
- Required Python packages:
  - win10toast
  - yt-dlp

## Setup

1. Install the required Python package:
```bash
pip install win10toast
```

2. Make sure you have yt-dlp installed and accessible in your PATH.

## Workflow

### 1. Create playlist_urls.txt
First, create a text file named `playlist_urls.txt` with one YouTube playlist URL per line. For example:
```
https://www.youtube.com/playlist?list=PLxxxxxxxx
https://www.youtube.com/playlist?list=PLyyyyyyyy
```

### 2. Extract Playlist Information
Run `yt_extract_playlists.py` to extract video information from your playlists:
```bash
python yt_extract_playlists.py
```
This will create a `playlists_videos.json` file containing all video information.

### 3. Download Videos
Run `yt_bulk_downloader.py` to download the videos:
```bash
python yt_bulk_downloader.py
```
This script will:
- Create a `videos` folder with subfolders for each playlist
- Download videos with proper naming and numbering
- Handle failed downloads and retries
- Show Windows notifications for errors and completion
- Create a `downloaded.txt` archive to track downloaded videos
- Create a `failed_downloads.txt` for any failed downloads

### 4. Extract Audio (Optional)
If you want to extract audio from the downloaded videos, run:
```bash
python yt_extract_audio.py
```
This will create an `audio` folder with MP3 files.

## Features

- **Automatic Retries**: Failed downloads are automatically retried
- **Progress Tracking**: Keeps track of downloaded videos to avoid duplicates
- **Error Handling**: Windows notifications for errors and completion
- **Cookie Management**: Uses Firefox cookies for authentication
- **Rate Limiting**: Implements sleep intervals to avoid rate limiting
- **File Organization**: Creates organized folder structure for videos and audio

## Notes

- Make sure you're logged into YouTube in Firefox before running the scripts
- The scripts use random user agents to avoid detection
- Failed downloads are saved in `failed_downloads.txt` and can be retried later
- Downloaded videos are tracked in `downloaded.txt` to avoid re-downloading

## Troubleshooting

If you encounter cookie-related errors:
1. Open Firefox
2. Go to YouTube and ensure you're logged in
3. Run the script again

For other issues, check the Windows notifications for error messages. 
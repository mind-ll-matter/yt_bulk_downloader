# YouTube Playlist Downloader

This repository contains three Python scripts that work together to download members-only videos from YouTube playlists. The scripts handle both video and audio downloads, with features like automatic retries, progress tracking, and Windows notifications.

## Prerequisites

- Python 3.x
- Firefox browser (for cookies)
- Required Python packages:
  - win10toast
  - yt-dlp
- FFmpeg (for video/audio processing)

## Setup

1. Create and activate a virtual environment (recommended):
   ```bash
   # Create virtual environment
   python -m venv venv

   # Activate virtual environment
   # On Windows PowerShell:
   .\venv\Scripts\Activate.ps1
   # On Windows Command Prompt:
   .\venv\Scripts\activate.bat
   # On Linux/Mac:
   source venv/bin/activate
   ```

2. Install the required Python package:
   ```bash
   pip install win10toast
   ```

3. Install yt-dlp:
   - **Windows**: Download the latest `yt-dlp.exe` from [yt-dlp releases](https://github.com/yt-dlp/yt-dlp/releases) and place it in your project directory or add it to your system PATH
   - **Linux/Mac**: Install via pip:
     ```bash
     pip install yt-dlp
     ```

4. Install FFmpeg:
   - **Windows**:
     1. Download FFmpeg from [FFmpeg official builds](https://www.gyan.dev/ffmpeg/builds/) (get the "essentials" build)
     2. Extract the downloaded zip file
     3. Copy `ffmpeg.exe`, `ffprobe.exe`, and `ffplay.exe` to your project directory or add the `bin` folder to your system PATH
   - **Linux**:
     ```bash
     sudo apt update
     sudo apt install ffmpeg
     ```
   - **Mac**:
     ```bash
     brew install ffmpeg
     ```

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
- FFmpeg is required for video/audio processing and must be accessible in your PATH or project directory

## Troubleshooting

If you encounter cookie-related errors:
1. Open Firefox
2. Go to YouTube and ensure you're logged in
3. Run the script again

If you get FFmpeg-related errors:
1. Verify FFmpeg is installed correctly by running `ffmpeg -version` in your terminal
2. Make sure FFmpeg executables are in your PATH or project directory
3. For Windows users, ensure you have both `ffmpeg.exe` and `ffprobe.exe`

For other issues, check the Windows notifications for error messages. 
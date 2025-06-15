import subprocess
import os
import time
import re
import json
import random
import sys
from win10toast import ToastNotifier

FAILED_FILE = "failed_downloads.txt"
DOWNLOAD_ARCHIVE = "downloaded.txt"
PLAYLISTS_JSON = "playlists_videos.json"

# Initialize Windows notification
toaster = ToastNotifier()

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:116.0) Gecko/20100101 Firefox/116.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_3_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
]

def sanitize_folder_name(name):
    # Replace invalid characters with safe alternatives
    # Using only alphanumeric, dash, underscore, and period
    replacements = {
        ':': '-',    # Colon becomes dash
        '/': '-',    # Forward slash becomes dash
        '\\': '-',   # Backslash becomes dash
        '?': '',     # Question mark removed
        '*': 'x',    # Asterisk becomes x
        '<': '-',    # Less than becomes dash
        '>': '-',    # Greater than becomes dash
        '|': '-',    # Pipe becomes dash
        '"': '',     # Double quote removed
        "'": '',     # Single quote removed
        '&': 'and',  # Ampersand becomes 'and'
        '@': 'at',   # At symbol becomes 'at'
        '#': '',     # Hash removed
        '$': '',     # Dollar sign removed
        '%': '',     # Percent sign removed
        '+': 'plus', # Plus becomes 'plus'
        ';': '-',    # Semicolon becomes dash
        '=': '-',    # Equals becomes dash
        '[': '(',    # Square bracket becomes parenthesis
        ']': ')',    # Square bracket becomes parenthesis
        '^': '',     # Caret removed
        '`': '',     # Backtick removed
        '{': '(',    # Curly brace becomes parenthesis
        '}': ')',    # Curly brace becomes parenthesis
        '~': '-',    # Tilde becomes dash
    }
    
    # Apply all replacements
    for char, replacement in replacements.items():
        name = name.replace(char, replacement)
    
    # Remove any double dashes that might have been created
    while '--' in name:
        name = name.replace('--', '-')
    
    # Remove any double spaces that might have been created
    name = ' '.join(name.split())
    
    # Remove leading/trailing dashes and spaces
    name = name.strip('- ')
    
    return name

def read_failed():
    if not os.path.exists(FAILED_FILE):
        return []
    with open(FAILED_FILE, "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip()]

def write_failed(failed_list):
    with open(FAILED_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(failed_list) + "\n" if failed_list else "")

def add_failed(entry):
    failed = read_failed()
    if entry not in failed:
        failed.append(entry)
        write_failed(failed)

def remove_failed(entry):
    failed = read_failed()
    if entry in failed:
        failed.remove(entry)
        write_failed(failed)

def notify_error(title, message):
    toaster.show_toast(
        title,
        message,
        duration=10,
        threaded=True
    )

def download_video(video_url, video_title, playlist_folder, index, retry_count=0):
    print(f"🎬 Downloading: {video_title}")
    user_agent = random.choice(USER_AGENTS)

    # Extract video ID from URL
    video_id = None
    if "youtube.com/watch?v=" in video_url:
        video_id = video_url.split("watch?v=")[1].split("&")[0]
    elif "youtu.be/" in video_url:
        video_id = video_url.split("youtu.be/")[1].split("?")[0]

    # Check if video is already in download archive
    skip_sleep = False
    if video_id and os.path.exists(DOWNLOAD_ARCHIVE):
        with open(DOWNLOAD_ARCHIVE, "r", encoding="utf-8") as f:
            if f"youtube {video_id}" in f.read():
                skip_sleep = True
                print("📝 Video already in download archive, skipping sleep interval")

    try:
        formatted_index = f"{index:02d}"
        safe_title = sanitize_folder_name(video_title)
        cmd = [
            "yt-dlp",
            "--cookies-from-browser", "firefox",
            "--user-agent", user_agent,
            "--download-archive", DOWNLOAD_ARCHIVE,
            "--throttled-rate", "500K",
            "--retries", "1",
            "--fragment-retries", "1",
            "--file-access-retries", "1",
            "--retry-sleep", "30",
            "-o", f"./videos/{playlist_folder}/{formatted_index} - {safe_title}.%(ext)s",
            video_url
        ]
        
        # Only add sleep interval if video is not in archive
        if not skip_sleep:
            cmd.extend(["--sleep-interval", "15", "--max-sleep-interval", "45"])
        
        result = subprocess.run(cmd, stderr=subprocess.PIPE, text=True, check=False)

        # Check for various error conditions
        error_output = result.stderr.lower()
        
        # Check for cookie warning
        if "cookies are no longer valid" in error_output:
            if retry_count < 1:  # Only retry once for cookie issues
                print("\n🔄 Cookie warning detected, retrying download once...")
                # time.sleep(10)  # Short pause before retry
                return download_video(video_url, video_title, playlist_folder, index, retry_count + 1)
            else:
                error_msg = "Cookie warning persists after retry. Please run the script again."
                print(f"\n⚠️ {error_msg}")
                notify_error("YouTube Downloader Error", error_msg)
                failed_entry = f"{playlist_folder}/{video_title} - {video_url}"
                add_failed(failed_entry)
                return False

        # Check for DNS resolution errors
        if "failed to resolve" in error_output or "getaddrinfo failed" in error_output:
            if retry_count < 1:  # Reduced to 1 retry for DNS issues
                print(f"\n🌐 DNS resolution error detected, retrying download after 60 seconds...")
                time.sleep(60)
                return download_video(video_url, video_title, playlist_folder, index, retry_count + 1)
            else:
                error_msg = f"DNS resolution failed after retry for: {video_title}"
                print(f"\n⚠️ {error_msg}")
                notify_error("YouTube Downloader Error", error_msg)
                failed_entry = f"{playlist_folder}/{video_title} - {video_url}"
                add_failed(failed_entry)
                return False

        if result.returncode != 0:
            raise subprocess.CalledProcessError(result.returncode, result.args, result.stdout, result.stderr)

        failed_lines = read_failed()
        for line in failed_lines:
            if line.startswith(f"{playlist_folder}/") and video_url in line:
                remove_failed(line)
            elif line.startswith(f"{playlist_folder}/{video_title} -"):
                remove_failed(line)

        return True
    except subprocess.CalledProcessError as e:
        error_msg = str(e).lower()
        if "cookies" in error_msg or "authentication" in error_msg:
            msg = "Cookie error detected. Please:\n1. Open Firefox\n2. Go to YouTube and make sure you're logged in\n3. Run this script again"
            print(f"\n⚠️ {msg}")
            notify_error("YouTube Downloader Error", msg)
            sys.exit(1)
        
        failed_entry = f"{playlist_folder}/{video_title} - {video_url}"
        add_failed(failed_entry)
        error_msg = f"Failed to download: {video_title}"
        print(f"❌ {error_msg}")
        notify_error("YouTube Downloader Error", error_msg)
        return False

def retry_failed(playlists):
    print("\n🔄 Retrying failed downloads...")
    failed_lines = read_failed()
    still_failed = []

    for line in failed_lines:
        if " - " not in line:
            continue
        folder_name, rest = line.split("/", 1)
        title, url = rest.rsplit(" - ", 1)
        folder_name = sanitize_folder_name(folder_name)
        
        # Find the index from the playlists data
        index = 1
        if folder_name in playlists:
            for i, video in enumerate(playlists[folder_name].get("videos", []), 1):
                if video.get("url") == url:
                    index = i
                    break
        
        success = download_video(url, title, folder_name, index)
        delay = random.randint(5, 20)
        print(f"⏳ Sleeping {delay}s...\n")
        time.sleep(delay)
        if not success:
            still_failed.append(line)

    if still_failed:
        print(f"\n⚠️ {len(still_failed)} videos still failed after retry. See {FAILED_FILE}")
    else:
        print("\n✅ All failed videos downloaded successfully on retry!")
        write_failed([])

def main():
    print("\n⚠️  Please ensure 'Do Not Disturb' is turned off to receive notifications if the script stops!")
    input("Press Enter to continue...")
    
    try:
        if not os.path.exists(PLAYLISTS_JSON):
            error_msg = f"{PLAYLISTS_JSON} not found. Run the extractor script first."
            print(f"❌ {error_msg}")
            notify_error("YouTube Downloader Error", error_msg)
            return

        with open(PLAYLISTS_JSON, "r", encoding="utf-8") as f:
            playlists = json.load(f)

        for playlist_name, data in playlists.items():
            playlist_folder = sanitize_folder_name(playlist_name)
            os.makedirs(f"videos/{playlist_folder}", exist_ok=True)
            print(f"\n📁 Processing playlist: {playlist_name}")

            for index, video in enumerate(data.get("videos", []), 1):
                title = video.get("title", "Unknown Title")
                url = video.get("url")
                if url:
                    download_video(url, title, playlist_folder, index)

        retry_failed(playlists)
        notify_error("YouTube Downloader", "All downloads completed!")
        print("\n🎉 All downloads completed successfully! \n You can now set sleep settings to previous values and reactivate Do Not Disturb.")
    except KeyboardInterrupt:
        print("\n⚠️ Script interrupted by user")
        notify_error("YouTube Downloader", "Script was interrupted by user")
    except Exception as e:
        error_msg = f"Script crashed with error: {str(e)}"
        print(f"\n❌ {error_msg}")
        notify_error("YouTube Downloader Error", error_msg)
    finally:
        notify_error("YouTube Downloader", "Script has stopped running")

if __name__ == "__main__":
    main()

import subprocess
import json
import os
import re

PLAYLISTS_FILE = "playlist_urls.txt"
OUTPUT_FILE = "playlists_videos.json"

def sanitize_name(name):
    return re.sub(r'[<>:"/\\|?*]', "", name)

def get_playlist_info(playlist_url, playlist_name=None):
    try:
        if playlist_name:
            playlist_title = playlist_name
        else:
            result = subprocess.run(
                [
                    "yt-dlp",
                    "--print", "%(playlist_title)s",
                    "--skip-download",
                    "--sleep-interval", "5",
                    "--max-sleep-interval", "15",
                    playlist_url,
                ],
                capture_output=True,
                text=True,
                check=True,
            )
            playlist_title = result.stdout.strip() or playlist_name or "UnknownPlaylist"
        playlist_title = sanitize_name(playlist_title)
    except Exception:
        playlist_title = "UnknownPlaylist"

    try:
        result = subprocess.run(
            [
                "yt-dlp",
                "--flat-playlist",
                "--print", "{\"title\":\"%(title)s\",\"id\":\"%(id)s\"}",
                "--sleep-interval", "5",
                "--max-sleep-interval", "15",
                playlist_url,
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        videos_raw = result.stdout.strip().split("\n")
        videos = []
        for line in videos_raw:
            if not line.strip():
                continue
            try:
                video_info = json.loads(line)
                full_url = f"https://www.youtube.com/watch?v={video_info['id']}"
                videos.append({"title": video_info['title'], "url": full_url})
            except json.JSONDecodeError:
                continue
    except Exception:
        videos = []

    return playlist_title, playlist_url, videos

def main():
    if not os.path.exists(PLAYLISTS_FILE):
        print(f"Error: {PLAYLISTS_FILE} not found.")
        return

    all_playlists = {}

    with open(PLAYLISTS_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]
        
    # Process lines in pairs (name, url)
    for i in range(0, len(lines), 2):
        if i + 1 >= len(lines):
            break
            
        playlist_name = lines[i]
        playlist_url = lines[i + 1]
        
        print(f"Processing playlist: {playlist_name}")
        title, url, videos = get_playlist_info(playlist_url, playlist_name)
        all_playlists[title] = {
            "url": url,
            "videos": videos
        }
        print(f"  Found {len(videos)} videos in '{title}'")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(all_playlists, f, indent=2, ensure_ascii=False)

    print(f"\nSaved all playlist info to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()

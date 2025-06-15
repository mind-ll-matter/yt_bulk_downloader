import os
import subprocess
import re

VIDEOS_DIR = "videos"
AUDIO_DIR = "audio"

def sanitize_filename(filename):
    # Remove extension and sanitize name
    name = os.path.splitext(filename)[0]
    return re.sub(r'[<>:"/\\|?*]', "", name)

def extract_audio_from_video(video_path, output_dir):
    base_name = sanitize_filename(os.path.basename(video_path))
    output_path = os.path.join(output_dir, base_name + ".mp3")

    os.makedirs(output_dir, exist_ok=True)

    if os.path.exists(output_path):
        print(f"🎧 Audio already exists for: {base_name}")
        return

    print(f"🎧 Extracting audio: {video_path} → {output_path}")
    try:
        subprocess.run(
            ["ffmpeg", "-i", video_path, "-q:a", "0", "-map", "a", output_path],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except subprocess.CalledProcessError:
        print(f"❌ Failed to extract audio from {video_path}")

def main():
    for root, _, files in os.walk(VIDEOS_DIR):
        for file in files:
            if file.endswith((".mp4", ".mkv", ".webm", ".flv")):
                video_path = os.path.join(root, file)
                # Create corresponding audio folder mirroring videos folder structure
                relative_path = os.path.relpath(root, VIDEOS_DIR)
                audio_folder = os.path.join(AUDIO_DIR, relative_path)
                extract_audio_from_video(video_path, audio_folder)

if __name__ == "__main__":
    main()

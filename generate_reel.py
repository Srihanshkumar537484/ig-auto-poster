"""
generate_reel.py
Turns assets/post.jpg into a short vertical (1080x1920) video with a slow
Ken-Burns zoom effect, using ffmpeg (already installed on GitHub Actions
ubuntu runners -- free, no extra libraries needed).

Optionally merges a random royalty-free background track from
assets/audio/ if that folder exists and has files in it.
"""
import os
import random
import subprocess

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMG_PATH = os.path.join(ASSETS_DIR, "post.jpg")
REEL_PATH = os.path.join(ASSETS_DIR, "reel.mp4")
AUDIO_DIR = os.path.join(ASSETS_DIR, "audio")

DURATION_SEC = 8
FPS = 30


def get_random_audio():
    """Return a random audio file path from assets/audio/, or None if missing/empty."""
    if not os.path.isdir(AUDIO_DIR):
        return None
    files = [
        f for f in os.listdir(AUDIO_DIR)
        if f.lower().endswith((".mp3", ".wav", ".m4a", ".aac"))
    ]
    if not files:
        return None
    return os.path.join(AUDIO_DIR, random.choice(files))


def generate():
    if not os.path.exists(IMG_PATH):
        raise FileNotFoundError("Run generate_post.py first to create post.jpg")

    total_frames = DURATION_SEC * FPS
    # zoompan: slow zoom-in from 1.0x to ~1.06x only (reduced from 1.15x
    # so text near the image edges doesn't get cropped out of frame),
    # output vertical 1080x1920
    filter_complex = (
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920,"
        f"zoompan=z='min(zoom+0.0003,1.06)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS}"
    )

    audio_path = get_random_audio()

    cmd = ["ffmpeg", "-y", "-loop", "1", "-i", IMG_PATH]

    if audio_path:
        cmd += ["-i", audio_path]

    cmd += ["-vf", filter_complex, "-t", str(DURATION_SEC)]

    if audio_path:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p",
                "-c:a", "aac", "-shortest"]
    else:
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p", "-an"]

    cmd += ["-movflags", "+faststart", REEL_PATH]

    subprocess.run(cmd, check=True)
    print(f"Saved reel: {REEL_PATH}" + (f" (audio: {os.path.basename(audio_path)})" if audio_path else " (no audio track found)"))
    return REEL_PATH


if __name__ == "__main__":
    generate()

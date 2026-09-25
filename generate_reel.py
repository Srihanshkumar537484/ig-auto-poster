"""
generate_reel.py
Turns assets/post.jpg into a short vertical (1080x1920) video with a slow
Ken-Burns zoom effect, using ffmpeg (already installed on GitHub Actions
ubuntu runners -- free, no extra libraries needed).

Fixed version: pads the square image with black bars top/bottom instead of
cropping the sides, so text never gets cut off out of frame.
"""
import os
import subprocess

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
IMG_PATH = os.path.join(ASSETS_DIR, "post.jpg")
REEL_PATH = os.path.join(ASSETS_DIR, "reel.mp4")

DURATION_SEC = 8
FPS = 30


def generate():
    if not os.path.exists(IMG_PATH):
        raise FileNotFoundError("Run generate_post.py first to create post.jpg")

    total_frames = DURATION_SEC * FPS
    # Pad the 1080x1080 image into a 1080x1920 canvas (black bars top/bottom)
    # so the full width -- and all the text -- stays inside frame. Then apply
    # a gentle zoom that slowly eats into the bars rather than cropping the
    # actual picture content.
    filter_complex = (
        f"scale=1080:1080,"
        f"pad=1080:1920:0:(1920-1080)/2:color=black,"
        f"zoompan=z='min(zoom+0.0007,1.15)':d={total_frames}:"
        f"x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':s=1080x1920:fps={FPS}"
    )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1",
        "-i", IMG_PATH,
        "-vf", filter_complex,
        "-t", str(DURATION_SEC),
        "-c:v", "libx264",
        "-pix_fmt", "yuv420p",
        "-movflags", "+faststart",
        REEL_PATH,
    ]
    subprocess.run(cmd, check=True)
    print(f"Saved reel: {REEL_PATH}")
    return REEL_PATH


if __name__ == "__main__":
    generate()
    

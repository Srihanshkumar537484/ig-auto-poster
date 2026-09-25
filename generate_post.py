"""
generate_post.py
Creates one square image (1080x1080) with a random line picked from
content_bank.py (category chosen by day-of-week so shayari/sad/motivational
rotate automatically), saved to assets/post.jpg + writes the matching
caption to assets/caption.txt for post_instagram.py to reuse.
"""
import os
import random
import textwrap
import datetime
import requests
from PIL import Image, ImageDraw, ImageFont

from content_bank import CATEGORIES

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
os.makedirs(ASSETS_DIR, exist_ok=True)

FONT_PATH = os.path.join(ASSETS_DIR, "font.ttf")
FONT_URL = (
    "https://raw.githubusercontent.com/google/fonts/main/ofl/poppins/Poppins-SemiBold.ttf"
)

# Rotate category by weekday so content stays varied automatically.
# Mon/Thu -> motivational, Tue/Fri -> shayari, Wed/Sat/Sun -> sad
WEEKDAY_CATEGORY = {
    0: "motivational",
    1: "shayari",
    2: "sad",
    3: "motivational",
    4: "shayari",
    5: "sad",
    6: "sad",
}

# A few dark gradient pairs so posts look aesthetic without needing images.
GRADIENTS = [
    ((20, 20, 30), (60, 20, 80)),
    ((10, 10, 10), (40, 40, 60)),
    ((30, 10, 20), (80, 30, 40)),
    ((15, 25, 35), (30, 60, 90)),
    ((25, 15, 35), (70, 40, 90)),
]

HASHTAGS = {
    "shayari": "#shayari #hindishayari #shayarilover #dillisheher #rekhta",
    "sad": "#sadshayari #sadquotes #dard #tanhai #emotional",
    "motivational": "#motivation #motivationalquotes #successmindset #hardwork #inspiration",
}


def ensure_font():
    if not os.path.exists(FONT_PATH):
        try:
            r = requests.get(FONT_URL, timeout=20)
            r.raise_for_status()
            with open(FONT_PATH, "wb") as f:
                f.write(r.content)
        except Exception:
            pass  # fall back to PIL default font if download fails
    return FONT_PATH if os.path.exists(FONT_PATH) else None


def make_gradient(size, top, bottom):
    w, h = size
    base = Image.new("RGB", size, top)
    draw = ImageDraw.Draw(base)
    for y in range(h):
        ratio = y / h
        r = int(top[0] + (bottom[0] - top[0]) * ratio)
        g = int(top[1] + (bottom[1] - top[1]) * ratio)
        b = int(top[2] + (bottom[2] - top[2]) * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b))
    return base


def draw_centered_text(img, text, font_path):
    w, h = img.size
    draw = ImageDraw.Draw(img)
    size = 62
    font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()

    wrapped = textwrap.fill(text, width=22)
    while True:
        bbox = draw.multiline_textbbox((0, 0), wrapped, font=font, spacing=14)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        # 560px max width -- keeps text inside the ~607px zone that
        # survives generate_reel.py's square-to-vertical crop, so it
        # never gets cut off left/right when shown as a reel.
        if tw <= 560 and th <= h - 260:
            break
        size -= 4
        if size < 28:
            break
        font = ImageFont.truetype(font_path, size) if font_path else ImageFont.load_default()

    x = (w - tw) / 2
    y = (h - th) / 2
    draw.multiline_text((x, y), wrapped, font=font, fill=(255, 255, 255),
                         align="center", spacing=14)

    # small watermark/handle placeholder at bottom
    small_font = ImageFont.truetype(font_path, 30) if font_path else ImageFont.load_default()
    draw.text((w / 2, h - 70), "✦", font=small_font, fill=(255, 255, 255), anchor="mm")
    return img


def generate(category=None):
    if category is None:
        category = WEEKDAY_CATEGORY[datetime.datetime.utcnow().weekday()]
    line = random.choice(CATEGORIES[category])

    top, bottom = random.choice(GRADIENTS)
    img = make_gradient((1080, 1080), top, bottom)
    font_path = ensure_font()
    img = draw_centered_text(img, line, font_path)

    img_path = os.path.join(ASSETS_DIR, "post.jpg")
    img.save(img_path, quality=92)

    caption = f"{line}\n.\n.\n.\n{HASHTAGS[category]}"
    with open(os.path.join(ASSETS_DIR, "caption.txt"), "w", encoding="utf-8") as f:
        f.write(caption)

    print(f"Category: {category}")
    print(f"Line: {line}")
    print(f"Saved image: {img_path}")
    return img_path, caption


if __name__ == "__main__":
    generate()

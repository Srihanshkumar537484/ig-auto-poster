"""
post_instagram.py
Publishes assets/post.jpg as a normal feed post and assets/reel.mp4 as a
Reel, using the Instagram Graph API (free -- Meta does not charge for this).

Required env vars (set as GitHub Actions secrets):
  IG_USER_ID       -> Instagram Business/Creator account's numeric ID
  IG_ACCESS_TOKEN  -> long-lived Page access token with instagram_content_publish
  GITHUB_REPOSITORY -> auto-provided by GitHub Actions, e.g. "user/repo"
  GITHUB_REF_NAME    -> auto-provided branch name, usually "main"

Instagram's API needs the media file at a PUBLIC url -- we use the raw
GitHub URL of the file we just committed & pushed to the repo (see the
workflow yml, which commits assets/ before this script runs).
"""
import os
import sys
import time
import requests

GRAPH_VERSION = "v19.0"
GRAPH_URL = f"https://graph.facebook.com/{GRAPH_VERSION}"

IG_USER_ID = os.environ.get("IG_USER_ID")
ACCESS_TOKEN = os.environ.get("IG_ACCESS_TOKEN")
REPO = os.environ.get("GITHUB_REPOSITORY")
BRANCH = os.environ.get("GITHUB_REF_NAME", "main")

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")


def raw_url(filename):
    return f"https://raw.githubusercontent.com/{REPO}/{BRANCH}/assets/{filename}?t={int(time.time())}"


def read_caption():
    path = os.path.join(ASSETS_DIR, "caption.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def require_env():
    missing = [k for k in ("IG_USER_ID", "IG_ACCESS_TOKEN", "GITHUB_REPOSITORY") if not os.environ.get(k)]
    if missing:
        print(f"Missing required env vars: {missing}")
        sys.exit(1)


def create_container(payload):
    r = requests.post(f"{GRAPH_URL}/{IG_USER_ID}/media", data=payload, timeout=30)
    if not r.ok:
        print(f"create_container failed: {r.status_code} {r.text}")
    r.raise_for_status()
    return r.json()["id"]


def wait_until_ready(container_id, timeout_sec=300, interval=10):
    """Poll status_code until FINISHED. Used for both images and reels now."""
    waited = 0
    while waited < timeout_sec:
        r = requests.get(
            f"{GRAPH_URL}/{container_id}",
            params={"fields": "status_code", "access_token": ACCESS_TOKEN},
            timeout=30,
        )
        r.raise_for_status()
        status = r.json().get("status_code")
        if status == "FINISHED":
            return True
        if status == "ERROR":
            raise RuntimeError(f"Container {container_id} failed processing")
        time.sleep(interval)
        waited += interval
    raise TimeoutError(f"Container {container_id} not ready after {timeout_sec}s")


def publish(container_id):
    r = requests.post(
        f"{GRAPH_URL}/{IG_USER_ID}/media_publish",
        data={"creation_id": container_id, "access_token": ACCESS_TOKEN},
        timeout=30,
    )
    if not r.ok:
        print(f"publish failed: {r.status_code} {r.text}")
    r.raise_for_status()
    return r.json()


def post_image(caption):
    print("Creating image container...")
    container_id = create_container({
        "image_url": raw_url("post.jpg"),
        "caption": caption,
        "access_token": ACCESS_TOKEN,
    })
    print(f"Container: {container_id}, waiting for processing...")
    wait_until_ready(container_id, timeout_sec=60, interval=5)
    print("Processing done, publishing...")
    result = publish(container_id)
    print(f"Image post published: {result}")


def post_reel(caption):
    print("Creating reel container...")
    container_id = create_container({
        "media_type": "REELS",
        "video_url": raw_url("reel.mp4"),
        "caption": caption,
        "share_to_feed": "true",
        "access_token": ACCESS_TOKEN,
    })
    print(f"Container: {container_id}, waiting for processing...")
    wait_until_ready(container_id)
    print("Processing done, publishing...")
    result = publish(container_id)
    print(f"Reel published: {result}")


if __name__ == "__main__":
    require_env()
    caption = read_caption()
    mode = sys.argv[1] if len(sys.argv) > 1 else "both"

    if mode in ("image", "both"):
        post_image(caption)
    if mode in ("reel", "both"):
        post_reel(caption)

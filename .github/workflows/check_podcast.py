import os
import json
import feedparser
import requests

FEED_URL = "https://www.youtube.com/feeds/videos.xml?channel_id=UCV3RNy8oEetrk-vPkFz9iHw"
STATE_FILE = "last_video.json"

DISCORD_WEBHOOK = os.environ["DISCORD_WEBHOOK"]


def load_last_video():
    if not os.path.exists(STATE_FILE):
        return None

    with open(STATE_FILE, "r") as f:
        data = json.load(f)

    return data.get("video_id")


def save_last_video(video_id):
    with open(STATE_FILE, "w") as f:
        json.dump({"video_id": video_id}, f)


def send_to_discord(video):
    title = video.get("title", "New SLB Show video")
    link = video.get("link")
    published = video.get("published", "")

    message = (
        "🏀 **NEW SLB SHOW EPISODE**\n\n"
        f"**{title}**\n\n"
        f"▶️ [Watch on YouTube]({link})"
    )

    response = requests.post(
        DISCORD_WEBHOOK,
        json={"content": message},
        timeout=30,
    )

    response.raise_for_status()


def main():
    feed = feedparser.parse(FEED_URL)

    if not feed.entries:
        print("No videos found.")
        return

    latest = feed.entries[0]
    video_id = latest.get("yt_videoid")

    if not video_id:
        print("Could not identify video ID.")
        return

    last_video = load_last_video()

    if last_video == video_id:
        print("No new video.")
        return

    print(f"New video found: {latest.get('title')}")

    # On the first run, record the latest video but don't post it.
    if last_video is None:
        save_last_video(video_id)
        print("First run — recording current video without posting.")
        return

    send_to_discord(latest)
    save_last_video(video_id)

    print("Posted to Discord.")


if __name__ == "__main__":
    main()

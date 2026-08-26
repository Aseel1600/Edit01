"""
daily_autonomous_production.py
Master Daily Autonomous Engine for OpenMontage Wildlife Shorts.

1. Picks next queued story from config/wildlife_story_queue.json
2. Verifies / downloads 1080p source footage
3. Renders 4:5 Ghost Blur vertical video with synchronized kinetic subtitles
4. Uploads to YouTube Data API v3 (if --upload flag passed)
5. Sends rich Discord & Telegram notification
6. Increments queue index
"""

import sys
import json
import argparse
import subprocess
import os
from pathlib import Path


def generate_varied_cta(story: dict) -> str:
    """Varied CTA per video — Gemini if key present, else templated. Story exactly 60s, outro after."""
    title = story.get("title", "")
    animal = story.get("animal", "wildlife")
    gemini_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or os.getenv("GOOGLE_GENAI_API_KEY")
    if gemini_key:
        try:
            import requests
            prompt = f"You are Wild Mechanics Shorts CTA writer. Story: '{title}' ({animal}). Write ONE punchy CTA 10-14 words, varied, tailored to this story, that tells viewers to follow/subscribe to Wild Mechanics. No hashtags, no quotes, just the sentence. Example for Scarface Jaguar: 'Scarface never misses. Follow Wild Mechanics for more apex hunts.'"
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={gemini_key}"
            payload = {"contents": [{"parts": [{"text": prompt}]}], "generationConfig": {"temperature": 0.9, "maxOutputTokens": 40}}
            r = requests.post(url, json=payload, timeout=10)
            if r.ok:
                txt = r.json()["candidates"][0]["content"]["parts"][0]["text"].strip().strip('"').strip("'")
                txt = txt.splitlines()[0].strip()
                if 5 < len(txt.split()) < 20 and "follow" in txt.lower():
                    return txt
        except Exception as e:
            print(f"[CTA-Gemini] fallback: {e}")
    templates = {
        "jaguar": "Scarface never misses. Follow Wild Mechanics for more apex hunts.",
        "macaque": "Snow monkeys beat the freeze. Follow Wild Mechanics for more.",
        "tiger": "The Queen never rests. Follow Wild Mechanics for more jungle reigns.",
        "cheetah": "Malaika's chase never ends. Follow Wild Mechanics for more.",
        "wolf": "The pack always returns. Follow Wild Mechanics for more.",
        "mantis": "The punch is just mechanics. Follow Wild Mechanics for more.",
        "iguana": "Escape is pure mechanics. Follow Wild Mechanics for more.",
        "flying fish": "The glide is pure mechanics. Follow Wild Mechanics for more.",
        "butcher": "The butcher always waits. Follow Wild Mechanics for more.",
        "dolphin": "Teamwork is mechanics. Follow Wild Mechanics for more ocean hunts.",
        "butcher_bird": "The butcher's hook waits. Follow Wild Mechanics for more.",
        "snow leopard": "The ghost never misses. Follow Wild Mechanics for more.",
        "glass frog": "Invisibility is mechanics. Follow Wild Mechanics for more.",
    }
    key = animal.lower()
    for k, v in templates.items():
        if k in key:
            return v
    generic = [
        f"{animal} secrets never end. Follow Wild Mechanics for more.",
        f"Nature's mechanics never stop. Follow Wild Mechanics for more.",
        f"One wild story, more to come. Follow Wild Mechanics.",
    ]
    return generic[hash(title) % len(generic)]

# UTF-8 stdout
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from lib.notifier import NotificationDispatcher
from tools.publishers.youtube_uploader import YouTubeUploader
from lib.documentary_source_downloader import DocumentarySourceDownloader

QUEUE_FILE = ROOT_DIR / "config" / "wildlife_story_queue.json"


def load_queue() -> dict:
    if not QUEUE_FILE.exists():
        raise FileNotFoundError(f"Queue file missing: {QUEUE_FILE}")
    with open(QUEUE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_queue(queue_data: dict):
    with open(QUEUE_FILE, "w", encoding="utf-8") as f:
        json.dump(queue_data, f, indent=2)


def main():
    parser = argparse.ArgumentParser(description="OpenMontage Daily Autonomous Short Producer")
    parser.add_argument("--upload", action="store_true", help="Upload rendered video directly to YouTube")
    parser.add_argument("--notify", action="store_true", default=True, help="Send Discord/Telegram notification")
    parser.add_argument("--story-id", type=str, default=None, help="Produce a specific story by ID instead of queue next")
    args = parser.parse_args()

    print("=" * 65)
    print("🦁 OPENMONTAGE DAILY AUTONOMOUS WILDLIFE ENGINE")
    print("=" * 65)

    queue = load_queue()
    stories = queue.get("stories", [])
    if not stories:
        print("[ERROR] No stories in queue.")
        sys.exit(1)

    idx = queue.get("current_index", 0)
    story = None

    if args.story_id:
        for s in stories:
            if s.get("id") == args.story_id:
                story = s
                break
        if not story:
            print(f"[ERROR] Story ID '{args.story_id}' not found.")
            sys.exit(1)
    else:
        idx = idx % len(stories)
        story = stories[idx]

    print(f"\n🎬 Processing Story [{story.get('id')}]: {story.get('title')}")
    print(f"🐾 Animal: {story.get('animal')}")
    print(f"⏱️ Duration: {story.get('duration')}s (Start: {story.get('start')}s)")

    # 1. Resolve Source Footage
    source_url_or_path = story.get("source_url")
    source_path = Path(source_url_or_path)

    if not source_path.exists():
        print(f"\n📥 Downloading source footage: {source_url_or_path}...")
        dl = DocumentarySourceDownloader()
        source_path = dl.download_from_url(
            source_url_or_path,
            animal=story.get("animal", "wildlife").lower().replace(" ", "_"),
            resolution="1080p",
        )
    print(f"✅ Source footage ready: {source_path}")

    # 2. Render Output — story exactly 60.0s, CTA outro (varied per video) appended after
    cta_text = generate_varied_cta(story)
    print(f"📣 CTA: {cta_text}")
    if story.get("passthrough"):
        print(f"\n⚡ Master + CTA outro (passthrough): {source_path.name}")
        output_dir = ROOT_DIR / "projects" / story.get("id") / "renders"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_mp4 = output_dir / f"{story.get('id')}_ghost_4_5.mp4"
        render_cmd = [
            sys.executable,
            str(ROOT_DIR / "scripts" / "create_source_vo_short.py"),
            "--source", str(source_path),
            "--start", str(story.get("start", 0.0)),
            "--duration", str(story.get("duration", 60.0)),
            "--framing", "ghost-4-5",
            "--output", str(output_mp4),
            "--cta", cta_text,
        ]
        res = subprocess.run(render_cmd, capture_output=True, text=True)
        if res.returncode != 0 or not output_mp4.exists():
            print(f"[ERROR] Passthrough CTA render failed {res.returncode}")
            print(res.stdout); print(res.stderr)
            sys.exit(1)
        print(f"🎉 Passthrough CTA render complete: {round(output_mp4.stat().st_size/(1024*1024),2)} MB")
    else:
        output_dir = ROOT_DIR / "projects" / story.get("id") / "renders"
        output_dir.mkdir(parents=True, exist_ok=True)
        output_mp4 = output_dir / f"{story.get('id')}_ghost_4_5.mp4"

        ass_path = ROOT_DIR / story.get("ass_file")
        if not ass_path.exists():
            print(f"[ERROR] ASS subtitle file missing: {ass_path}")
            sys.exit(1)

        print(f"\n⚡ Rendering 4:5 Ghost Blur Short (60s story + CTA outro): {output_mp4.name}...")
        render_cmd = [
            sys.executable,
            str(ROOT_DIR / "scripts" / "create_source_vo_short.py"),
            "--source", str(source_path),
            "--start", str(story.get("start", 0.0)),
            "--duration", str(story.get("duration", 60.0)),
            "--ass", str(ass_path),
            "--framing", "ghost-4-5",
            "--output", str(output_mp4),
            "--cta", cta_text,
        ]
        res = subprocess.run(render_cmd, capture_output=True, text=True)
        if res.returncode != 0 or not output_mp4.exists():
            print(f"[ERROR] Render failed with exit code {res.returncode}")
            print("--- STDOUT ---")
            print(res.stdout)
            print("--- STDERR ---")
            print(res.stderr)
            sys.exit(1)

        print(f"🎉 Render complete! Output file size: {round(output_mp4.stat().st_size / (1024*1024), 2)} MB")

    # 3. Optional Upload to YouTube
    video_url = None
    if args.upload:
        print("\n🚀 Uploading to YouTube Shorts via YouTube Data API v3...")
        uploader = YouTubeUploader()
        up_res = uploader.execute({
            "video_path": str(output_mp4),
            "title": story.get("title"),
            "description": story.get("description"),
            "tags": story.get("tags", []),
            "privacy_status": "public",
        })
        if up_res.success:
            video_url = up_res.data.get("video_url")
            print(f"✅ Published to YouTube: {video_url}")
        else:
            print(f"⚠️ YouTube upload warning: {up_res.error}")

        # Optional Upload to Facebook Reels
        try:
            from tools.publishers.facebook_uploader import FacebookReelsUploader
            fb = FacebookReelsUploader()
            if fb.is_configured():
                print("\n📱 Uploading to Facebook Reels via Meta Graph API...")
                fb_res = fb.upload_reel(
                    video_path=str(output_mp4),
                    title=story.get("title", ""),
                    description=story.get("description", "")
                )
                if fb_res:
                    print(f"✅ Published to Facebook Reels: {fb_res.get('fb_url')}")
            else:
                print("\n[FB_UPLOADER] Facebook credentials not set in secrets; skipping FB Reels.")
        except Exception as fb_err:
            print(f"⚠️ Facebook upload warning: {fb_err}")

    # 4. Dispatch Discord / Telegram Notification
    if args.notify:
        print("\n🔔 Sending Discord / Telegram notification...")
        notifier = NotificationDispatcher()
        notifier.notify_video_published(
            title=story.get("title"),
            animal=story.get("animal"),
            duration_s=story.get("duration", 60.0),
            video_url=video_url,
        )

    # 5. Increment queue index if automatic run
    if not args.story_id:
        queue["current_index"] = (idx + 1) % len(stories)
        save_queue(queue)
        print(f"\n📋 Queue advanced: Next story is #{queue['current_index'] + 1} ({stories[queue['current_index']]['title']})")

    print("\n" + "=" * 65)
    print("✅ Autonomous daily production cycle completed!")
    print("=" * 65)


if __name__ == "__main__":
    main()

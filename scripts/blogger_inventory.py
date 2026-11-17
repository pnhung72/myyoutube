"""Kiểm kho công xưởng Blogger: bài học nào có video, bài nào thiếu nút dẫn sang YouTube,
video YouTube nào chưa được nhúng vào bài học nào.
Cần: blog_url trong config/settings.json + bật Blogger API v3 cho API key.
Ghi: data/public/lessons.json, data/public/gaps.json
"""
import re
from datetime import datetime, timezone

import requests

from common import api_key, cfg, load, save

API = "https://www.googleapis.com/blogger/v3"
VID = re.compile(r"(?:youtube(?:-nocookie)?\.com/embed/|youtube\.com/watch\?v=|youtu\.be/)([A-Za-z0-9_-]{11})")


def get(path, **params):
    params["key"] = api_key()
    r = requests.get(f"{API}/{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def fetch_all(blog_id, kind):
    items, token = [], None
    while True:
        extra = {"pageToken": token} if token else {}
        r = get(f"blogs/{blog_id}/{kind}", maxResults=500, fetchBodies="true", **extra)
        items += r.get("items", [])
        token = r.get("nextPageToken")
        if not token:
            return items


def main():
    c = cfg()
    url = (c.get("blog_url") or "").strip()
    if not url:
        print("Chưa điền blog_url trong config/settings.json - bỏ qua kiểm kho Blogger.")
        return
    blog_id = get("blogs/byurl", url=url)["id"]
    raw = fetch_all(blog_id, "posts")
    try:
        raw += fetch_all(blog_id, "pages")
    except requests.HTTPError:
        pass

    handle = c["channel_handle"].lstrip("@").lower()
    lessons = []
    for it in raw:
        html = it.get("content", "")
        low = html.lower()
        lessons.append({
            "title": it["title"], "url": it["url"], "labels": it.get("labels", []),
            "published": it["published"], "updated": it["updated"],
            "video_ids": sorted(set(VID.findall(html))),
            "has_cta": "sub_confirmation" in low or f"youtube.com/@{handle}" in low or "youtube.com/playlist" in low,
        })

    videos = load("data/public/videos.json", [])
    embedded = {vid for l in lessons for vid in l["video_ids"]}
    with_video = [l for l in lessons if l["video_ids"]]
    gaps = {
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "blog_items": len(lessons),
        "with_video": len(with_video),
        "without_video": [{"title": l["title"], "url": l["url"]} for l in lessons if not l["video_ids"]][:50],
        "missing_cta": [{"title": l["title"], "url": l["url"]} for l in with_video if not l["has_cta"]],
        "videos_not_embedded": [{"title": v["title"], "url": v["url"], "views": v["views"]}
                                for v in sorted(videos, key=lambda v: -v["views"]) if v["id"] not in embedded],
    }
    save("data/public/lessons.json", lessons)
    save("data/public/gaps.json", gaps)
    print(f"Blog: {len(lessons)} bài/trang, {len(with_video)} có video nhúng.")
    print(f" - {len(gaps['missing_cta'])} bài có video nhưng CHƯA có nút dẫn sang YouTube/đăng ký.")
    print(f" - {len(gaps['videos_not_embedded'])} video YouTube chưa được nhúng vào bài học nào.")


if __name__ == "__main__":
    main()
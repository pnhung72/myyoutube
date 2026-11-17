"""Kéo toàn bộ video công khai, gắn chủ đề, phát hiện trùng lặp.
Ghi: data/public/videos.json, channel.json, topics.json, duplicates.json
"""
import re
import unicodedata
from datetime import datetime, timezone
from difflib import SequenceMatcher

import requests

from common import api_key, cfg, save

API = "https://www.googleapis.com/youtube/v3"


def get(path, **params):
    params["key"] = api_key()
    r = requests.get(f"{API}/{path}", params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def seconds(iso):
    m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", iso or "")
    if not m:
        return 0
    h, mi, s = (int(x or 0) for x in m.groups())
    return h * 3600 + mi * 60 + s


def norm(text):
    text = unicodedata.normalize("NFD", text.lower().replace("đ", "d"))
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def topics_of(v, topics):
    hay = norm(" ".join([v["title"], v["description"], " ".join(v["tags"])]))
    found = [t for t, kws in topics.items() if any(norm(k) in hay for k in kws)]
    return found or ["khac"]


def find_duplicates(videos, threshold):
    pairs = []
    for i, a in enumerate(videos):
        na = norm(a["title"])
        for b in videos[i + 1:]:
            ratio = SequenceMatcher(None, na, norm(b["title"])).ratio()
            same_len = abs(a["duration"] - b["duration"]) <= 2
            if ratio >= threshold or (same_len and ratio >= 0.6):
                keep, review = (a, b) if a["views"] >= b["views"] else (b, a)
                pairs.append({
                    "similarity": round(ratio, 2), "same_duration": same_len,
                    "keep": keep["id"], "keep_title": keep["title"], "keep_views": keep["views"],
                    "review": review["id"], "review_title": review["title"], "review_views": review["views"],
                })
    return sorted(pairs, key=lambda p: -p["similarity"])


def main():
    c = cfg()
    ch = get("channels", part="snippet,statistics,contentDetails", id=c["channel_id"])["items"][0]
    uploads = ch["contentDetails"]["relatedPlaylists"]["uploads"]

    ids, token = [], None
    while True:
        extra = {"pageToken": token} if token else {}
        r = get("playlistItems", part="contentDetails", playlistId=uploads, maxResults=50, **extra)
        ids += [i["contentDetails"]["videoId"] for i in r["items"]]
        token = r.get("nextPageToken")
        if not token:
            break

    videos = []
    for i in range(0, len(ids), 50):
        r = get("videos", part="snippet,statistics,contentDetails", id=",".join(ids[i:i + 50]))
        for it in r["items"]:
            s, st = it["snippet"], it.get("statistics", {})
            v = {
                "id": it["id"], "title": s["title"], "description": s.get("description", ""),
                "tags": s.get("tags", []), "published": s["publishedAt"],
                "duration": seconds(it["contentDetails"].get("duration")),
                "views": int(st.get("viewCount", 0)), "likes": int(st.get("likeCount", 0)),
                "comments": int(st.get("commentCount", 0)),
            }
            v["topics"] = topics_of(v, c["topics"])
            videos.append(v)
    videos.sort(key=lambda v: v["published"], reverse=True)

    out = [{
        "id": v["id"], "title": v["title"], "published": v["published"], "duration": v["duration"],
        "views": v["views"], "likes": v["likes"], "comments": v["comments"], "topics": v["topics"],
        "tags": v["tags"], "desc": v["description"][:300],
        "thumb": f"https://i.ytimg.com/vi/{v['id']}/hqdefault.jpg",
        "url": f"https://www.youtube.com/watch?v={v['id']}",
    } for v in videos]

    by_topic = {}
    for v in videos:
        for t in v["topics"]:
            by_topic.setdefault(t, []).append(v["id"])

    st = ch["statistics"]
    save("data/public/videos.json", out)
    save("data/public/topics.json", by_topic)
    save("data/public/duplicates.json", find_duplicates(videos, c["duplicate_threshold"]))
    save("data/public/channel.json", {
        "title": ch["snippet"]["title"], "handle": c["channel_handle"],
        "subscribers": None if st.get("hiddenSubscriberCount") else int(st.get("subscriberCount", 0)),
        "views": int(st.get("viewCount", 0)), "video_count": int(st.get("videoCount", 0)),
        "updated": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    })
    print(f"OK: {len(out)} video, {len(by_topic)} chủ đề.")


if __name__ == "__main__":
    main()
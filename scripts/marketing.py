"""Nhân viên marketing: soạn sẵn bài đăng Blogger cho video mới + nhắc chiến dịch theo mùa.
Ghi: data/public/posts/<id>.html, posts.json, campaigns.json, site.json
"""
from datetime import date, datetime, timezone
from html import escape

from common import ROOT, cfg, load, save

LATEST = 10


def post_html(v, c):
    shop = c["shop"]
    sub = f"https://www.youtube.com/{c['channel_handle']}?sub_confirmation=1"
    parts = [
        f'<p>{escape(v["desc"].splitlines()[0]) if v["desc"] else escape(v["title"])}</p>',
        f'<div style="position:relative;padding-bottom:56.25%;height:0"><iframe style="position:absolute;top:0;left:0;width:100%;height:100%" '
        f'src="https://www.youtube-nocookie.com/embed/{v["id"]}?rel=0" title="{escape(v["title"])}" frameborder="0" allowfullscreen></iframe></div>',
        f'<p>▶ <a href="{v["url"]}" target="_blank" rel="noopener">Xem trên YouTube</a> · '
        f'🔔 <a href="{sub}" target="_blank" rel="noopener">Đăng ký kênh để nhận bài mới</a><br>'
        f'💬 Có thắc mắc? Hãy bình luận dưới video trên YouTube, thầy sẽ trả lời.</p>',
    ]
    if shop.get("zalo") or shop.get("url"):
        link = shop.get("url") or f'https://zalo.me/{shop["zalo"]}'
        parts.append(f'<hr><p>🐟 <b>{escape(shop["name"])}</b> - {escape(shop["desc"])} '
                     f'<a href="{escape(link)}" target="_blank" rel="noopener">Đặt hàng</a></p>')
    return "\n".join(parts)


def next_date(month, day, today):
    d = date(today.year, month, day)
    return d if d >= today else date(today.year + 1, month, day)


def main():
    c = cfg()
    videos = load("data/public/videos.json", [])
    posts = load("data/public/posts.json", [])
    done = {p["id"] for p in posts}

    for v in videos[:LATEST]:
        if v["id"] in done:
            continue
        f = ROOT / "data" / "public" / "posts" / f"{v['id']}.html"
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(post_html(v, c), encoding="utf-8")
        labels = [t for t in v["topics"] if t != "khac"] + ["Nhạc sáng tác"]
        posts.append({"id": v["id"], "title": v["title"], "labels": labels,
                      "file": f"posts/{v['id']}.html", "created": datetime.now(timezone.utc).isoformat(timespec="seconds")})
        print("Bài blog mới soạn:", v["title"])
    save("data/public/posts.json", posts)

    today = date.today()
    upcoming = []
    for ev in c["seasonal"]:
        d = next_date(ev["month"], ev["day"], today)
        left = (d - today).days
        if left <= 60:
            upcoming.append({"name": ev["name"], "date": d.isoformat(), "days_left": left, "idea": ev["idea"]})
    upcoming.sort(key=lambda e: e["days_left"])
    chan = f"https://www.youtube.com/{c['channel_handle']}"
    footer = (
        '<div style="border:2px solid #c2185b;border-radius:10px;padding:12px;margin:16px 0;background:#fff5f9">'
        '<b>👉 Xem bài này trên YouTube để:</b><ul>'
        '<li>Xem tiếp cả playlist cùng lớp, không bị gián đoạn</li>'
        '<li>Đặt câu hỏi ngay dưới video - thầy sẽ trả lời</li>'
        '<li>Nhận thông báo khi có bài giảng mới</li></ul>'
        f'<a href="{chan}/playlists" target="_blank" rel="noopener">▶ Xem playlist trên YouTube</a> &nbsp; '
        f'<a href="{chan}?sub_confirmation=1" target="_blank" rel="noopener">🔔 Đăng ký kênh</a></div>'
    )
    (ROOT / "data" / "public" / "lesson_footer.html").write_text(footer, encoding="utf-8")
    save("data/public/campaigns.json", {"updated": today.isoformat(), "upcoming": upcoming})
    save("data/public/site.json", {"handle": c["channel_handle"], "shop": c["shop"]})
    for e in upcoming:
        print(f"Sắp tới: {e['name']} còn {e['days_left']} ngày - {e['idea']}")


if __name__ == "__main__":
    main()
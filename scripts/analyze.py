"""Phân tích xu hướng từ dữ liệu công khai và đề xuất cải thiện.
Ghi: data/public/analysis.json
"""
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from statistics import median

from common import load, save

NAMES = ["Thứ 2", "Thứ 3", "Thứ 4", "Thứ 5", "Thứ 6", "Thứ 7", "Chủ nhật"]


def parse(iso):
    return datetime.fromisoformat(iso.replace("Z", "+00:00"))


def main():
    videos = load("data/public/videos.json", [])
    if not videos:
        raise SystemExit("Chưa có videos.json - chạy sync trước.")
    now = datetime.now(timezone.utc)
    med = median(v["views"] for v in videos)
    total_views = sum(v["views"] for v in videos) or 1
    comment_rate = round(sum(v["comments"] for v in videos) / total_views * 100, 3)
    like_rate = round(sum(v["likes"] for v in videos) / total_views * 100, 2)

    topic_stats = defaultdict(list)
    weekday = defaultdict(list)
    for v in videos:
        for t in v["topics"]:
            topic_stats[t].append(v["views"])
        weekday[(parse(v["published"]) + timedelta(hours=7)).weekday()].append(v["views"])

    topics = sorted(
        ({"topic": t, "videos": len(x), "avg_views": round(sum(x) / len(x))} for t, x in topic_stats.items()),
        key=lambda d: -d["avg_views"],
    )
    days = sorted(
        ({"day": NAMES[d], "videos": len(x), "avg_views": round(sum(x) / len(x))} for d, x in weekday.items()),
        key=lambda d: -d["avg_views"],
    )
    weak = [v for v in videos if (now - parse(v["published"])).days >= 30 and v["views"] < med * 0.5]

    tips = []
    if topics:
        tips.append(f"Chủ đề hiệu quả nhất: '{topics[0]['topic']}' (TB {topics[0]['avg_views']} lượt xem). Làm thêm video cùng chủ đề.")
    if days and len(videos) >= 10:
        tips.append(f"Ngày đăng có TB lượt xem cao nhất: {days[0]['day']} (mẫu nhỏ, hãy thử nghiệm thêm).")
    if comment_rate < 0.3:
        tips.append("Tỉ lệ bình luận thấp: cuối video đặt 1 câu hỏi (vd: 'Bài hát nhắc bạn đến thầy cô nào?') và ghim bình luận.")
    if weak:
        tips.append(f"{len(weak)} video thấp hơn nửa mức trung vị sau 30 ngày: thử đổi thumbnail/tiêu đề, thêm vào playlist chủ đề.")
    tips.append("Mỗi video: vào bài hát trong 10 giây đầu, đặt từ khóa chính ở đầu tiêu đề, thêm thẻ + màn hình kết thúc.")

    save("data/public/analysis.json", {
        "updated": now.isoformat(timespec="seconds"), "median_views": med,
        "comment_rate_pct": comment_rate, "like_rate_pct": like_rate,
        "top": [{"id": v["id"], "title": v["title"], "views": v["views"]} for v in sorted(videos, key=lambda v: -v["views"])[:5]],
        "weak": [{"id": v["id"], "title": v["title"], "views": v["views"]} for v in weak[:10]],
        "topics": topics, "weekdays": days, "tips": tips,
    })
    print("Gợi ý:")
    for t in tips:
        print(" -", t)


if __name__ == "__main__":
    main()
"""Theo dõi tiến độ điều kiện kiếm tiền (YPP).
Giờ xem 12 tháng và 28 ngày: nhập tay vào config/settings.json (lấy từ YouTube Studio > Phân tích).
Ghi: data/private/monetization.json (KHÔNG đưa lên GitHub)
"""
from datetime import date, datetime, timedelta, timezone

from common import cfg, load, save

DEADLINE = date(2027, 2, 1)  # từ ngày này, người nộp đơn mới cần 8.000 giờ
TIERS = [
    ("Hỗ trợ fan (500 sub + 3.000 giờ + 3 video/90 ngày)", 500, 3000),
    ("Quảng cáo - mốc HIỆN TẠI (1.000 sub + 4.000 giờ)", 1000, 4000),
    ("Quảng cáo - mốc MỚI từ 1/2/2027 (1.000 sub + 8.000 giờ)", 1000, 8000),
]


def main():
    c = cfg()
    ch = load("data/public/channel.json", {})
    videos = load("data/public/videos.json", [])
    subs = c.get("subscribers_override") or ch.get("subscribers") or 0
    h12, h28 = c["watch_hours_12m"], c["watch_hours_28d"]
    left = (DEADLINE - date.today()).days
    projected = h12 + (h28 / 28 * left if left > 0 else 0)
    cutoff = datetime.now(timezone.utc) - timedelta(days=90)
    up90 = sum(1 for v in videos if datetime.fromisoformat(v["published"].replace("Z", "+00:00")) >= cutoff)

    rows = []
    print(f"Subscriber: {subs} | Giờ xem 12 tháng: {h12} | Video đăng 90 ngày: {up90}")
    print(f"Còn {left} ngày đến 1/2/2027 | Dự kiến giờ xem lúc đó: {round(projected)}\n")
    for name, need_s, need_h in TIERS:
        row = {"tier": name, "subs_pct": min(100, round(subs / need_s * 100)),
               "hours_pct": min(100, round(h12 / need_h * 100)),
               "on_track_by_deadline": subs >= need_s and projected >= need_h}
        rows.append(row)
        print(f"- {name}\n    sub {row['subs_pct']}% | giờ xem {row['hours_pct']}% | kịp trước 1/2/2027: {'CÓ' if row['on_track_by_deadline'] else 'chưa'}")
    save("data/private/monetization.json", {"subs": subs, "hours_12m": h12, "uploads_90d": up90,
                                            "days_to_deadline": left, "projected_hours": round(projected), "tiers": rows})
    print("\nLưu ý: cần không có gậy cảnh cáo + tuân thủ chính sách kiếm tiền. Tuyệt đối không mua sub/view.")


if __name__ == "__main__":
    main()
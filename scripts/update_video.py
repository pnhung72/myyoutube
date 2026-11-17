"""Sửa hoặc xóa 1 video (luôn sao lưu trước, luôn hỏi xác nhận).

Ví dụ:
  python scripts/update_video.py VIDEO_ID --title "Tiêu đề mới" --description "Mô tả" --tags "nhạc,thầy cô"
  python scripts/update_video.py VIDEO_ID --privacy private      # ẩn bản trùng (nên dùng thay vì xóa)
  python scripts/update_video.py VIDEO_ID --delete                # xóa hẳn (không hoàn tác)
"""
import argparse
import datetime
import json
import sys

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build

from common import ROOT


def service():
    tok = ROOT / "secrets" / "token.json"
    if not tok.exists():
        sys.exit("Chạy .\\run.ps1 auth trước.")
    creds = Credentials.from_authorized_user_file(str(tok))
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
        tok.write_text(creds.to_json(), encoding="utf-8")
    return build("youtube", "v3", credentials=creds)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("video_id")
    ap.add_argument("--title")
    ap.add_argument("--description")
    ap.add_argument("--tags", help="cách nhau bằng dấu phẩy")
    ap.add_argument("--privacy", choices=["public", "unlisted", "private"])
    ap.add_argument("--delete", action="store_true")
    a = ap.parse_args()

    yt = service()
    items = yt.videos().list(part="snippet,status", id=a.video_id).execute()["items"]
    if not items:
        sys.exit("Không tìm thấy video (hoặc không thuộc kênh đang đăng nhập).")
    v = items[0]
    stamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    backup = ROOT / "backups" / f"{a.video_id}-{stamp}.json"
    backup.parent.mkdir(exist_ok=True)
    backup.write_text(json.dumps(v, ensure_ascii=False, indent=1), encoding="utf-8")
    print("Đã sao lưu:", backup.name, "| Video:", v["snippet"]["title"])

    if a.delete:
        if input("Gõ XOA để xóa vĩnh viễn (mất lượt xem, bình luận, giờ xem): ") != "XOA":
            sys.exit("Hủy.")
        yt.videos().delete(id=a.video_id).execute()
        print("Đã xóa.")
        return

    if a.title:
        v["snippet"]["title"] = a.title
    if a.description is not None:
        v["snippet"]["description"] = a.description
    if a.tags:
        v["snippet"]["tags"] = [t.strip() for t in a.tags.split(",") if t.strip()]
    if a.privacy:
        v["status"]["privacyStatus"] = a.privacy
    print("Sẽ cập nhật:", v["snippet"]["title"], "| quyền riêng tư:", v["status"]["privacyStatus"])
    if input("Đồng ý? (y/n): ").lower() != "y":
        sys.exit("Hủy.")
    body = {"id": a.video_id, "snippet": v["snippet"], "status": v["status"]}
    yt.videos().update(part="snippet,status", body=body).execute()
    print("Đã cập nhật.")


if __name__ == "__main__":
    main()
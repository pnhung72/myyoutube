"""Đăng nhập Google 1 lần trên laptop (để sửa/xóa video). Lưu secrets/token.json.
Cần secrets/client_secret.json (OAuth client loại "Desktop app" tạo ở Google Cloud).
"""
from google_auth_oauthlib.flow import InstalledAppFlow

from common import ROOT

SCOPES = ["https://www.googleapis.com/auth/youtube.force-ssl"]
secret = ROOT / "secrets" / "client_secret.json"
if not secret.exists():
    raise SystemExit("Chưa có secrets/client_secret.json - xem hướng dẫn cuối bài.")
creds = InstalledAppFlow.from_client_secrets_file(str(secret), SCOPES).run_local_server(port=0)
(ROOT / "secrets" / "token.json").write_text(creds.to_json(), encoding="utf-8")
print("Đã lưu secrets/token.json")
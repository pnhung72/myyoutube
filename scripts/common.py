"""Hàm dùng chung."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def cfg():
    return json.loads((ROOT / "config" / "settings.json").read_text(encoding="utf-8"))


def api_key():
    key = os.environ.get("YT_API_KEY", "").strip()
    env = ROOT / "secrets" / ".env"
    if not key and env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.startswith("YT_API_KEY="):
                key = line.split("=", 1)[1].strip()
    if not key:
        raise SystemExit("Thiếu YT_API_KEY (đặt trong secrets/.env hoặc GitHub Secrets).")
    return key


def save(rel, obj):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1), encoding="utf-8")


def load(rel, default=None):
    p = ROOT / rel
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_web_push_notification.py
-----------------------------------------------------------------------------
Bắn thông báo đẩy (Web Push) qua OneSignal REST API mỗi khi xuất bản ấn bản mới.
Yêu cầu:
  - ONESIGNAL_APP_ID (hoặc cấu hình trong fintech-intelligence/push-config.json)
  - ONESIGNAL_REST_API_KEY (biến môi trường)
-----------------------------------------------------------------------------
"""

import os
import sys
import json
import urllib.request
import urllib.error

WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"
EDITION_JSON = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "edition-data.json")
PUSH_CONFIG_JSON = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "push-config.json")


def main():
    app_id = os.environ.get("ONESIGNAL_APP_ID", "").strip()
    if not app_id and os.path.exists(PUSH_CONFIG_JSON):
        with open(PUSH_CONFIG_JSON, "r", encoding="utf-8") as f:
            app_id = (json.load(f).get("oneSignalAppId") or "").strip()

    rest_key = os.environ.get("ONESIGNAL_REST_API_KEY", "").strip()
    if not app_id or not rest_key:
        print("ℹ️ Chưa cấu hình ONESIGNAL_APP_ID hoặc ONESIGNAL_REST_API_KEY — bỏ qua gửi Web Push.")
        return

    with open(EDITION_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    ed_num = data.get("editionNumber", "Bnews")
    ed_date = data.get("editionDate", "")
    cover = data.get("editorialSections", {}).get("sec02_coverStory", {})
    headline = cover.get("editorialHeadline", "Ấn bản tài chính mới đã xuất bản")

    payload = {
        "app_id": app_id,
        "included_segments": ["Subscribed Users"],
        "headings": {"vi": f"Bnews · {ed_num} ({ed_date})", "en": f"Bnews · {ed_num} ({ed_date})"},
        "contents": {"vi": headline, "en": headline},
        "url": "https://bryanportfolio.io.vn/fintech-intelligence/",
        "chrome_web_icon": "https://bryanportfolio.io.vn/fintech-intelligence/fintech-favicon-192.png",
    }

    req = urllib.request.Request(
        "https://api.onesignal.com/notifications",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Content-Type": "application/json; charset=utf-8",
            "Authorization": f"Key {rest_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            print("✅ Đã gửi Web Push:", resp.status, resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        print(f"❌ Lỗi gửi Web Push ({e.code}):", e.read().decode("utf-8"))
        sys.exit(1)


if __name__ == "__main__":
    main()

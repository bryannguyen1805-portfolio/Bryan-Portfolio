#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_web_push_notification.py
-----------------------------------------------------------------------------
Gửi Web Push Notification hàng loạt qua Firebase Cloud Messaging (FCM)
cho tất cả độc giả đã đăng ký trong Firestore collection `fcm_tokens`.

Yêu cầu:
  - pip install firebase-admin
  - GOOGLE_APPLICATION_CREDENTIALS=/path/to/bnews-firebase-adminsdk.json
    (hoặc đặt file tại ~/.gemini/config/firebase/bnews-11b05-service-account.json)
-----------------------------------------------------------------------------
"""

import os
import sys
import json

WORKSPACE_ROOT = "/Users/quangtri/Documents/Bryan-Portfolio-Antigravity"
EDITION_JSON = os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "edition-data.json")
DEFAULT_SA_PATH = os.path.expanduser("~/.gemini/config/firebase/bnews-11b05-service-account.json")


def main():
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS", "").strip() or DEFAULT_SA_PATH
    if not os.path.exists(cred_path):
        print(f"ℹ️ Chưa có Firebase Service Account JSON tại {cred_path} — bỏ qua gửi FCM Push.")
        return

    try:
        import firebase_admin
        from firebase_admin import credentials, firestore, messaging
    except ImportError:
        print("❌ Thiếu thư viện `firebase-admin`. Cài bằng: pip3 install firebase-admin")
        sys.exit(1)

    if not firebase_admin._apps:
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)

    db = firestore.client()
    docs = list(db.collection("fcm_tokens").stream())
    tokens = [d.to_dict().get("token") for d in docs if d.to_dict().get("token")]
    if not tokens:
        print("ℹ️ Chưa có thiết bị nào đăng ký nhận thông báo trong `fcm_tokens`.")
        return

    with open(EDITION_JSON, "r", encoding="utf-8") as f:
        data = json.load(f)

    ed_num = data.get("editionNumber", "Bnews")
    ed_date = data.get("editionDate", "")
    cover = data.get("editorialSections", {}).get("sec02_coverStory", {})
    headline = cover.get("editorialHeadline", "Ấn bản tài chính mới đã xuất bản")
    target_url = "https://bryanportfolio.io.vn/fintech-intelligence/"

    total_sent = 0
    invalid_doc_ids = []
    # FCM multicast supports up to 500 tokens per batch
    for i in range(0, len(tokens), 500):
        batch_tokens = tokens[i : i + 500]
        batch_docs = docs[i : i + 500]
        msg = messaging.MulticastMessage(
            tokens=batch_tokens,
            notification=messaging.Notification(
                title=f"Bnews · {ed_num} ({ed_date})",
                body=headline,
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="https://bryanportfolio.io.vn/fintech-intelligence/fintech-favicon-192.png",
                    badge="https://bryanportfolio.io.vn/fintech-intelligence/fintech-favicon-32.png",
                ),
                fcm_options=messaging.WebpushFCMOptions(link=target_url),
            ),
        )
        resp = messaging.send_each_for_multicast(msg)
        total_sent += resp.success_count
        for idx, r in enumerate(resp.responses):
            if not r.success and r.exception and getattr(r.exception, "code", "") in (
                "UNREGISTERED",
                "INVALID_ARGUMENT",
                "messaging/registration-token-not-registered",
            ):
                invalid_doc_ids.append(batch_docs[idx].id)

    for doc_id in invalid_doc_ids:
        db.collection("fcm_tokens").document(doc_id).delete()

    print(f"✅ Đã gửi Firebase Web Push thành công tới {total_sent}/{len(tokens)} thiết bị (đã dọn {len(invalid_doc_ids)} token hết hạn).")


if __name__ == "__main__":
    main()

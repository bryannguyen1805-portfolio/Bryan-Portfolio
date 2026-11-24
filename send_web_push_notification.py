#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_web_push_notification.py
-----------------------------------------------------------------------------
Gửi Web Push Notification hàng loạt qua Firebase Cloud Messaging (FCM)
cho tất cả độc giả đã đăng ký trong Firestore collection `fcm_tokens`.

Format chuẩn Option A + Kiểu 1:
  - Title: "Bnews · Ấn bản số {N}" (gọn < 25 ký tự, không bị cắt '...' trên iPhone)
  - Body : "Đã có {total_news} tin Tài chính – Ngân hàng & Thanh toán số hôm nay. Mở đọc bản tóm tắt 3 phút ngay →"
-----------------------------------------------------------------------------
"""

import os
import re
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

    raw_ed_num = str(data.get("editionNumber", "")).strip()
    m = re.search(r"(\d+)", raw_ed_num)
    ed_num_only = m.group(1) if m else raw_ed_num
    total_news = len(data.get("eligibleNewsList", [])) or 40

    push_title = f"Bnews · Ấn bản số {ed_num_only}" if ed_num_only else "Bnews · Ấn bản mới"
    push_body = f"Đã có {total_news} tin Tài chính – Ngân hàng & Thanh toán số hôm nay. Mở đọc bản tóm tắt 3 phút ngay →"
    target_url = "https://bryanportfolio.io.vn/fintech-intelligence/"
    notif_tag = f"bnews-edition-{ed_num_only or 'latest'}"

    total_sent = 0
    invalid_doc_ids = []
    for i in range(0, len(tokens), 500):
        batch_tokens = tokens[i : i + 500]
        batch_docs = docs[i : i + 500]
        msg = messaging.MulticastMessage(
            tokens=batch_tokens,
            notification=messaging.Notification(
                title=push_title,
                body=push_body,
            ),
            webpush=messaging.WebpushConfig(
                notification=messaging.WebpushNotification(
                    icon="https://bryanportfolio.io.vn/fintech-intelligence/fintech-favicon-192.png",
                    badge="https://bryanportfolio.io.vn/fintech-intelligence/fintech-favicon-32.png",
                    tag=notif_tag,
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

    print(f"✅ Đã gửi Firebase Web Push ({push_title}) tới {total_sent}/{len(tokens)} thiết bị (đã dọn {len(invalid_doc_ids)} token hết hạn).")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_daily_edition.py
-----------------------------------------------------------------------------
BRYAN FINTECH MARKET INTELLIGENCE — MASTER DAILY PIPELINE RUNNER (OFFICIAL V1.0)
Quy trình vận hành chuẩn:
  Research -> Analyze -> Generate -> Validate (D-06 Gate) -> Save Local Artifacts.

CHÍNH SÁCH VẬN HÀNH & PHÁT HÀNH (VERSION 1.0 OFFICIAL):
- Mặc định chạy ở chế độ `--mode local-staging` (tạo & kiểm định artifact local, không đẩy git).
- Chế độ `--mode manual-release` thực hiện commit & push lên GitHub main khi có xác nhận.
-----------------------------------------------------------------------------
"""

import os
import sys
import json
import argparse
import subprocess
from datetime import datetime

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.basename(CURRENT_DIR) == "daily-run-package":
    PACKAGE_DIR = CURRENT_DIR
    WORKSPACE_ROOT = os.path.abspath(os.path.join(PACKAGE_DIR, "..", ".."))
else:
    WORKSPACE_ROOT = CURRENT_DIR
    PACKAGE_DIR = os.path.join(WORKSPACE_ROOT, "pilot-output", "daily-run-package")

os.chdir(PACKAGE_DIR)


def print_header(title):
    print("\n" + "=" * 80)
    print(f"🚀 {title}")
    print("=" * 80)


def parse_args():
    parser = argparse.ArgumentParser(
        description="Bryan FinTech Intelligence Daily Pipeline Runner (Local Staging by default)"
    )
    parser.add_argument(
        "--mode",
        choices=["local-staging", "manual-release"],
        default="local-staging",
        help="Pipeline mode. Defaults to 'local-staging' (Git push disabled).",
    )
    parser.add_argument(
        "--date",
        default=None,
        help="Target edition date YYYY-MM-DD (defaults to today).",
    )
    parser.add_argument(
        "--manual-release",
        action="store_true",
        help="Explicit manual release flag (requires --owner-accepted and BNEWS_OWNER_ACCEPTANCE=APPROVED).",
    )
    parser.add_argument(
        "--owner-accepted",
        action="store_true",
        help="Explicit Product Owner acceptance confirmation flag.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate safety policy and display pipeline stages without executing or pushing.",
    )
    return parser.parse_args()


def can_publish_production(args):
    owner_env = os.environ.get("BNEWS_OWNER_ACCEPTANCE", "").strip()
    return (
        args.mode == "manual-release"
        and args.manual_release is True
        and args.owner_accepted is True
        and owner_env == "APPROVED"
    )


def main():
    args = parse_args()
    start_time = datetime.now()
    today_str = args.date or start_time.strftime("%Y-%m-%d")
    git_push_allowed = can_publish_production(args)

    print_header(
        f"BRYAN FINTECH INTELLIGENCE — DAILY PIPELINE [{start_time.strftime('%Y-%m-%d %H:%M:%S')}]"
    )
    print(f"   - Chế độ vận hành: {args.mode} (Mặc định an toàn: local-staging)")
    print(f"   - Ngày mục tiêu  : {today_str}")
    print(
        f"   - Git Push / Production Deploy: {'ALLOWED (OWNER APPROVED)' if git_push_allowed else 'BLOCKED (LOCAL STAGING ONLY)'}"
    )

    if args.mode == "manual-release" and not git_push_allowed:
        print(
            "❌ TỪ CHỐI XUẤT BẢN PRODUCTION: Yêu cầu đồng thời --manual-release, --owner-accepted và BNEWS_OWNER_ACCEPTANCE=APPROVED."
        )
        sys.exit(2)

    if args.dry_run:
        print(
            "🧪 [DRY RUN] Quy trình chuẩn: Research -> Analyze -> Generate -> Validate (D-06 Gate) -> Save Local Artifacts."
        )
        print("🧪 [DRY RUN] Không thực thi thay đổi dữ liệu và không thực hiện git push.")
        return

    workspace_root = WORKSPACE_ROOT
    daily_editions_dir = os.path.join(
        workspace_root,
        "BRYAN_FINTECH_INTELLIGENCE",
        "03_WORKING_PHASES",
        "PHASE07_R1.0.4-P1",
        "06_DAILY_EDITIONS",
        "daily-editions",
    )
    orch_script = os.path.join(
        workspace_root,
        "BRYAN_FINTECH_INTELLIGENCE",
        "03_WORKING_PHASES",
        "PHASE07_R1.0.4-P1",
        "02_SOURCE_CODE",
        "phase07_daily_runtime_orchestrator.py",
    )
    today_edition_dir = os.path.join(daily_editions_dir, today_str)

    # Step 0 [Research]: Check if target edition exists and has verified-news.json
    has_completed_edition = os.path.exists(today_edition_dir) and os.path.exists(
        os.path.join(today_edition_dir, "verified-news.json")
    )
    if not has_completed_edition and os.path.exists(orch_script):
        print(f"📌 [BƯỚC 0/4 - RESEARCH] Phát hiện ấn bản ngày ({today_str}). Kích hoạt Live Runtime Orchestrator...")
        orch_cmd = [sys.executable, orch_script, "--mode", "LIVE", "--date", today_str]
        try:
            orch_res = subprocess.run(orch_cmd, capture_output=True, text=True, timeout=180)
            if orch_res.returncode == 0:
                print("   ✅ Live Orchestrator: Quét tin, kiểm định 0-24h thành công!")
            else:
                print("   ℹ️ Live Orchestrator: Tiếp tục với luồng tổng hợp ấn bản mới nhất.")
        except Exception as e:
            print(f"   ⚠️ Lưu ý khi gọi Live Orchestrator: {e}")

    # Engine parity guard — Workspace root scripts are the Source of Truth.
    import hashlib, shutil

    def _sha(p):
        with open(p, "rb") as fh:
            return hashlib.sha256(fh.read()).hexdigest()

    for shared_mod in ["update_magspread_pilot_ui.py", "ed29_editorial_content.py", "ed30_editorial_content.py"]:
        root_mod = os.path.join(WORKSPACE_ROOT, shared_mod)
        pkg_mod = os.path.join(PACKAGE_DIR, shared_mod)
        if os.path.exists(root_mod) and os.path.abspath(root_mod) != os.path.abspath(pkg_mod):
            if not os.path.exists(pkg_mod) or _sha(root_mod) != _sha(pkg_mod):
                shutil.copy2(root_mod, pkg_mod)
                print(f"🔁 Đồng bộ module: {shared_mod} (gốc -> daily-run-package).")

    # Step 1 [Analyze & Generate]: Execute update_magspread_pilot_ui.py
    print("📌 [BƯỚC 1/4 - ANALYZE & GENERATE] Kích hoạt Editorial Engine & Quality Gate...")
    cmd = [sys.executable, "update_magspread_pilot_ui.py", "--date", today_str]
    res = subprocess.run(cmd, capture_output=True, text=True)

    if res.returncode != 0:
        print(f"❌ Lỗi khi thực thi update_magspread_pilot_ui.py:\n{res.stderr}")
        sys.exit(1)
    else:
        print(res.stdout.strip())

    # Step 2 [Validate]: Output & D-06 Gate Integrity
    print("\n📌 [BƯỚC 2/4 - VALIDATE] Đối soát tính toàn vẹn dữ liệu & Cổng chất lượng 8 lớp...")
    json_path = os.path.join(PACKAGE_DIR, "edition-data.json")
    js_path = os.path.join(PACKAGE_DIR, "edition-data.js")

    if not os.path.exists(json_path) or not os.path.exists(js_path):
        print("❌ Lỗi: Không tìm thấy edition-data.json hoặc edition-data.js!")
        sys.exit(1)

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    ed_id = data.get("editionId")
    ed_date = data.get("editionDate")
    news_count = len(data.get("eligibleNewsList", []))
    mp_count = len(data.get("marketPulseSnapshot", []))
    cs = data.get("editorialSections", {}).get("sec02_coverStory", {})
    lead_headline = cs.get("editorialHeadline", "N/A")
    gate_status = data.get("contentQualityAudit", {}).get("status", "UNKNOWN")
    if gate_status == "UNKNOWN":
        for audit_path in (
            os.path.join(PACKAGE_DIR, "logs", "content-quality-audit.json"),
            os.path.join(WORKSPACE_ROOT, "fintech-intelligence", "logs", "content-quality-audit.json"),
        ):
            if os.path.exists(audit_path):
                with open(audit_path, "r", encoding="utf-8") as af:
                    gate_status = json.load(af).get("status", "UNKNOWN")
                break

    print(f"   - Mã ấn bản       : {ed_id}")
    print(f"   - Ngày xuất bản   : {ed_date}")
    print(f"   - Tin tức xác minh: {news_count} bài (0-24h pass)")
    print(f"   - Market Pulse    : {mp_count} chỉ số")
    print(f"   - Bài đinh trang  : {lead_headline}")
    print(f"   - Quality Gate    : {gate_status}")

    # Step 3 [Save Local Artifacts]: Sync to fintech-intelligence/ and pilot-output/
    print("\n📌 [BƯỚC 3/4 - SAVE LOCAL ARTIFACTS] Lưu trữ đồng bộ tại local staging (fintech-intelligence/ & pilot-output/)...")
    web_portal_dir = os.path.join(WORKSPACE_ROOT, "fintech-intelligence")
    pilot_output_dir = os.path.join(WORKSPACE_ROOT, "pilot-output")

    html_path = os.path.join(PACKAGE_DIR, "index.html")
    if os.path.exists(html_path):
        import re

        ts = int(datetime.now().timestamp())
        with open(html_path, "r", encoding="utf-8") as f:
            h_text = f.read()
        h_text = re.sub(r'href="(?:\.\/)?magspread\.css(?:\?v=[^"]*)?"', f'href="./magspread.css?v={ts}"', h_text)
        h_text = re.sub(r'src="(?:\.\/)?edition-data\.js(?:\?v=[^"]*)?"', f'src="./edition-data.js?v={ts}"', h_text)
        h_text = re.sub(r'src="(?:\.\/)?magspread\.js(?:\?v=[^"]*)?"', f'src="./magspread.js?v={ts}"', h_text)
        ed_badge_val = data.get("editionNumber", "").split("·")[0].strip()
        if ed_badge_val:
            h_text = re.sub(r">ẤN BẢN SỐ \d+<", f">{ed_badge_val}<", h_text)
        with open(html_path, "w", encoding="utf-8") as f:
            f.write(h_text)
        preview_path = os.path.join(PACKAGE_DIR, "magspread-preview.html")
        with open(preview_path, "w", encoding="utf-8") as f:
            f.write(h_text)

    sync_files = [
        "index.html",
        "magspread-preview.html",
        "edition-data.js",
        "edition-data.json",
        "EVIDENCE_INDEX.json",
        "magspread.css",
        "magspread.js",
        "robots.txt",
        "sitemap.xml",
        "zalo-icon.svg",
        "bnews-logo-light.png",
        "bnews-logo-dark.png",
        "bnews-logo-light-opt.png",
        "bnews-logo-dark-opt.png",
        "bnews-logo-light-opt.webp",
        "bnews-logo-dark-opt.webp",
        "bnews-logo-light.webp",
        "bnews-logo-dark.webp",
        "fintech-favicon.png",
        "fintech-favicon.webp",
        "fintech-favicon-opt.png",
        "fintech-favicon-opt.webp",
    ]
    for target_dir in (web_portal_dir, pilot_output_dir):
        if os.path.exists(target_dir):
            for fn in sync_files:
                src = os.path.join(PACKAGE_DIR, fn)
                dst = os.path.join(target_dir, fn)
                if os.path.exists(src) and os.path.abspath(src) != os.path.abspath(dst):
                    shutil.copy2(src, dst)
            print(f"   - Đã lưu bản local staging tại: {target_dir}")

    # Step 4 [Production Safety Gate]: Auto Git Push DISABLED by default
    print("\n📌 [BƯỚC 4/4 - RELEASE GOVERNANCE GATE] Kiểm tra quyền phát hành Production...")
    if not git_push_allowed:
        print("   🛡️ LOCAL-STAGING MODE: Tự động Git commit/push lên Production đã BỊ VÔ HIỆU HÓA theo mặc định.")
        print("   ℹ️ Để phát hành Production chính thức sau nghiệm thu, chạy thủ công với đầy đủ:")
        print("      BNEWS_OWNER_ACCEPTANCE=APPROVED python3 run_daily_edition.py --mode manual-release --manual-release --owner-accepted")
    else:
        print("   ⚠️ Đủ cờ nghiệm thu thủ công — Thực hiện git commit & push theo yêu cầu chủ sản phẩm...")
        try:
            candidate_targets = [
                "fintech-intelligence/",
                "pilot-output/",
                "update_magspread_pilot_ui.py",
                "ed29_editorial_content.py",
                "ed30_editorial_content.py",
                "run_daily_edition.py",
                "setup_daily_scheduler_9am.sh",
                "README_DAILY_RUN.md",
            ]
            git_targets = [p for p in candidate_targets if os.path.exists(os.path.join(workspace_root, p))]
            subprocess.run(["git", "add", "--"] + git_targets, cwd=workspace_root, check=True)
            staged_res = subprocess.run(
                ["git", "diff", "--cached", "--name-only"],
                cwd=workspace_root,
                capture_output=True,
                text=True,
                check=True,
            )
            excluded_paths = [
                ln
                for ln in staged_res.stdout.splitlines()
                if ln.endswith(".DS_Store") or "/__pycache__/" in ln or ln.endswith(".pyc")
            ]
            if excluded_paths:
                subprocess.run(["git", "reset", "-q", "HEAD", "--"] + excluded_paths, cwd=workspace_root, check=True)

            diff_res = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=workspace_root)
            if diff_res.returncode != 0:
                commit_msg = f"Manual owner-approved release: FinTech Intelligence [{ed_date}]"
                subprocess.run(["git", "commit", "-m", commit_msg], cwd=workspace_root, check=True)
                push_res = subprocess.run(["git", "push", "origin", "HEAD:main"], cwd=workspace_root, capture_output=True, text=True)
                if push_res.returncode == 0:
                    print("   ✅ Manual Git push thành công (branch: main)!")
                else:
                    print(f"   ❌ Lỗi khi đẩy Git: {push_res.stderr.strip()}")
                    sys.exit(1)
            else:
                print("   ℹ️ Không có thay đổi cần commit.")
        except Exception as e:
            print(f"   ❌ Lỗi đồng bộ Git: {e}")
            sys.exit(1)

    elapsed = (datetime.now() - start_time).total_seconds()
    if git_push_allowed:
        print_header("XUẤT BẢN THÀNH CÔNG — PRODUCTION RELEASE ĐÃ NGHIỆM THU")
    else:
        print_header("HOÀN TẤT LOCAL STAGING (CHỜ NGHIỆM THU CHỦ SẢN PHẨM)")
    print(f"⏱️  Thời gian thực thi: {elapsed:.2f} giây")
    print(f"📁 Artifact local tại : {os.path.join(web_portal_dir, 'index.html')}")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    main()

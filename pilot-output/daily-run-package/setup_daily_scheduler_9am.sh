#!/bin/bash
# =============================================================================
# BRYAN FINTECH INTELLIGENCE — DAILY SCHEDULER SETUP (9:00 AM EVERY DAY)
# =============================================================================
set -e

PACKAGE_DIR="/Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package"
PLIST_FILE="$HOME/Library/LaunchAgents/com.bryan.fintech.dailyrun.plist"
LOG_DIR="$PACKAGE_DIR/logs"

mkdir -p "$LOG_DIR"

echo "================================================================="
echo "🚀 THIẾT LẬP LỊCH TỰ ĐỘNG CHẠY HÀNG NGÀY LÚC 9:00 AM (macOS)"
echo "================================================================="

# 1. Tạo file launchd plist (Chuẩn tối ưu của Apple macOS)
cat << 'EOF' > "$PLIST_FILE"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bryan.fintech.dailyrun</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package/run_daily_edition.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package/logs/daily_run.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/quangtri/Documents/Bryan-Portfolio-Antigravity/pilot-output/daily-run-package/logs/daily_run_error.log</string>
    <key>RunAtLoad</key>
    <false/>
</dict>
</plist>
EOF

# 2. Nạp dịch vụ vào launchctl
launchctl unload "$PLIST_FILE" 2>/dev/null || true
launchctl load "$PLIST_FILE"

echo "✅ Đã tạo và kích hoạt dịch vụ LaunchAgent: $PLIST_FILE"
echo "⏰ Thời gian chạy tự động: 09:00 AM mỗi ngày."
echo "📝 Nhật ký hoạt động sẽ được ghi vào: $LOG_DIR/daily_run.log"
echo "🌐 Ấn bản sau khi chạy sẽ tự động cập nhật tại: $PACKAGE_DIR/index.html"
echo "================================================================="
echo "🎉 HOÀN TẤT CÀI ĐẶT! BẠN KHÔNG CẦN LÀM GÌ THÊM."
echo "================================================================="

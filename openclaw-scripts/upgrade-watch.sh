#!/bin/bash
# ============================================================
# OpenClaw 升级监控钩子
# 用途：监控OpenClaw版本变化，升级后自动备份+恢复前端注入
# 部署：crontab每5分钟执行一次
# 位置：虚拟机 /home/xzy0626/.openclaw/scripts/upgrade-watch.sh
# ============================================================

SCRIPTS_DIR="/home/xzy0626/.openclaw/scripts"
VERSION_FILE="/home/xzy0626/.openclaw/last_known_version.txt"
LOG_FILE="/home/xzy0626/.openclaw/upgrade-watch.log"
OPENCLAW_UI="/usr/lib/node_modules/openclaw/dist/control-ui"

# 获取当前版本
CURRENT_VERSION=$(openclaw --version 2>/dev/null | head -1 || echo "unknown")

# 读取上次已知版本
LAST_VERSION=""
if [ -f "$VERSION_FILE" ]; then
    LAST_VERSION=$(cat "$VERSION_FILE")
fi

# 首次运行，记录版本
if [ -z "$LAST_VERSION" ]; then
    echo "$CURRENT_VERSION" > "$VERSION_FILE"
    echo "$(date) [INIT] 首次运行，记录版本: $CURRENT_VERSION" >> "$LOG_FILE"
    exit 0
fi

# 版本未变化
if [ "$CURRENT_VERSION" = "$LAST_VERSION" ]; then
    # 但检查前端注入是否还在（可能被其他原因覆盖）
    if ! grep -q "model-selector-v2.js" "${OPENCLAW_UI}/index.html" 2>/dev/null; then
        echo "$(date) [REPAIR] 前端注入丢失，执行恢复..." >> "$LOG_FILE"
        bash "${SCRIPTS_DIR}/restore.sh" >> "$LOG_FILE" 2>&1
    fi
    exit 0
fi

# 版本变化了！执行升级后恢复流程
echo "$(date) [UPGRADE] 检测到版本变化: $LAST_VERSION -> $CURRENT_VERSION" >> "$LOG_FILE"

# 1. 先备份（用旧版本的备份作为基准）
echo "$(date) [UPGRADE] 执行备份..." >> "$LOG_FILE"
bash "${SCRIPTS_DIR}/backup.sh" >> "$LOG_FILE" 2>&1

# 2. 恢复前端注入
echo "$(date) [UPGRADE] 执行恢复..." >> "$LOG_FILE"
bash "${SCRIPTS_DIR}/restore.sh" >> "$LOG_FILE" 2>&1

# 3. 重启Gateway
echo "$(date) [UPGRADE] 重启Gateway..." >> "$LOG_FILE"
openclaw gateway restart >> "$LOG_FILE" 2>&1

# 4. 更新版本记录
echo "$CURRENT_VERSION" > "$VERSION_FILE"

echo "$(date) [UPGRADE] 升级后恢复完成！" >> "$LOG_FILE"

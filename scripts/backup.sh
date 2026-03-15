#!/bin/bash
# ============================================================
# OpenClaw 前端自定义文件 备份脚本
# 用途：备份OpenClaw前端注入的自定义文件到本地和远程
# 位置：虚拟机 /home/xzy0626/.openclaw/scripts/backup.sh
# ============================================================

set -e

BACKUP_DIR="/home/xzy0626/.openclaw/backups"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${TIMESTAMP}"
OPENCLAW_UI="/usr/lib/node_modules/openclaw/dist/control-ui"
OPENCLAW_CONFIG="/home/xzy0626/.openclaw"

echo "=========================================="
echo "  OpenClaw 备份 - ${TIMESTAMP}"
echo "=========================================="

# 创建备份目录
mkdir -p "${BACKUP_PATH}/control-ui"
mkdir -p "${BACKUP_PATH}/config"

# 备份前端文件
echo "[1/4] 备份前端文件..."
cp "${OPENCLAW_UI}/index.html" "${BACKUP_PATH}/control-ui/" 2>/dev/null || echo "  跳过: index.html不存在"
cp "${OPENCLAW_UI}/assets/model-selector-v2.js" "${BACKUP_PATH}/control-ui/" 2>/dev/null || echo "  跳过: model-selector-v2.js不存在"

# 备份配置文件
echo "[2/4] 备份配置文件..."
cp "${OPENCLAW_CONFIG}/openclaw.json" "${BACKUP_PATH}/config/" 2>/dev/null || echo "  跳过: openclaw.json不存在"
cp "${OPENCLAW_CONFIG}/exec-approvals.json" "${BACKUP_PATH}/config/" 2>/dev/null || echo "  跳过: exec-approvals.json不存在"

# 记录当前版本
echo "[3/4] 记录版本信息..."
openclaw --version > "${BACKUP_PATH}/version.txt" 2>/dev/null || echo "unknown" > "${BACKUP_PATH}/version.txt"
date >> "${BACKUP_PATH}/version.txt"

# 清理超过30天的旧备份
echo "[4/4] 清理旧备份..."
find "${BACKUP_DIR}" -maxdepth 1 -type d -mtime +30 -exec rm -rf {} \; 2>/dev/null || true

echo ""
echo "✅ 备份完成: ${BACKUP_PATH}"
ls -la "${BACKUP_PATH}/"
echo ""
echo "备份目录中共有 $(ls -1d ${BACKUP_DIR}/*/ 2>/dev/null | wc -l) 个备份"

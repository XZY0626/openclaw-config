#!/bin/bash
# verify_agents.sh — 验证 AGENTS.md 完整性
# 用法: bash verify_agents.sh [--update]
# --update: 重新计算并更新 checksum（在主人批准修改后使用）

WORKSPACE="/home/xzy0626/.openclaw/workspace"
AGENTS_MD="$WORKSPACE/AGENTS.md"
CHECKSUM_FILE="$WORKSPACE/.agents_checksum"

if [ "$1" = "--update" ]; then
    SHA256=$(sha256sum "$AGENTS_MD" | awk '{print $1}')
    sed -i "s/^SHA256=.*/SHA256=$SHA256/" "$CHECKSUM_FILE"
    echo "[CHECKSUM UPDATED] New hash: $SHA256"
    echo "Updated at: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$CHECKSUM_FILE"
    exit 0
fi

# 校验模式
if [ ! -f "$CHECKSUM_FILE" ]; then
    echo "[FAIL] Checksum file not found: $CHECKSUM_FILE"
    exit 2
fi

EXPECTED=$(grep "^SHA256=" "$CHECKSUM_FILE" | cut -d= -f2)
ACTUAL=$(sha256sum "$AGENTS_MD" | awk '{print $1}')

if [ "$EXPECTED" = "$ACTUAL" ]; then
    echo "[OK] AGENTS.md integrity verified (sha256 match)"
    exit 0
else
    echo "[ALERT] AGENTS.md HAS BEEN MODIFIED!"
    echo "  Expected: $EXPECTED"
    echo "  Actual:   $ACTUAL"
    echo "  If this was intentional, run: bash $0 --update"
    exit 1
fi

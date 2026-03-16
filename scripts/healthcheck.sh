#!/bin/bash
# healthcheck.sh — OpenClaw Guardian Core G1 启动健康检查
# 版本：v1.0 | 创建：2026-03-16 (WorkBuddy signed)
# 用途：龙虾新会话启动时可选执行，快速验证核心安全状态

set -euo pipefail

PASS=0
WARN=0
FAIL=0

check() {
    local name="$1"
    local status="$2"  # pass/warn/fail
    local msg="$3"
    case "$status" in
        pass) echo "[PASS] $name: $msg"; ((PASS++)) ;;
        warn) echo "[WARN] $name: $msg"; ((WARN++)) ;;
        fail) echo "[FAIL] $name: $msg"; ((FAIL++)) ;;
    esac
}

echo "=== OpenClaw Healthcheck v1.0 ==="
echo "时间: $(date '+%Y-%m-%d %H:%M:%S')"
echo ""

# G1.1 AGENTS.md 完整性
if [ -f ~/.openclaw/workspace/.agents_checksum ] && [ -f ~/.openclaw/workspace/verify_agents.sh ]; then
    result=$(bash ~/.openclaw/workspace/verify_agents.sh 2>&1 || true)
    if echo "$result" | grep -q "PASS\|校验通过\|OK"; then
        check "AGENTS.md checksum" pass "校验通过"
    else
        check "AGENTS.md checksum" fail "校验失败或被篡改！result=$result"
    fi
else
    check "AGENTS.md checksum" warn "verify_agents.sh 或 .agents_checksum 不存在"
fi

# G1.2 .pre-disable-auth 不存在
if [ ! -f ~/.openclaw/.pre-disable-auth ]; then
    check "Gateway 认证" pass ".pre-disable-auth 不存在，认证强制生效"
else
    check "Gateway 认证" fail ".pre-disable-auth 存在！认证已被旁路！立即删除！"
fi

# G1.3 Gateway 进程
if pgrep -f "openclaw-gateway\|openclaw gateway" > /dev/null 2>&1; then
    check "Gateway 进程" pass "运行中"
else
    check "Gateway 进程" warn "Gateway 未运行"
fi

# G1.4 Gateway 端口绑定
if ss -tlnp 2>/dev/null | grep -q "127.0.0.1:18789"; then
    check "Gateway 端口绑定" pass "127.0.0.1:18789（本地回环）"
elif netstat -tlnp 2>/dev/null | grep -q "127.0.0.1:18789"; then
    check "Gateway 端口绑定" pass "127.0.0.1:18789（本地回环）"
else
    check "Gateway 端口绑定" warn "18789 端口未监听或工具不可用"
fi

# G1.5 供应链：denylist 验证
if python3 -c "
import json, sys
try:
    d = json.load(open('/home/xzy0626/.openclaw/openclaw.json'))
    dl = d.get('skills', {}).get('denylist', [])
    sys.exit(0 if 'clawhub/*' in dl else 1)
except: sys.exit(2)
" 2>/dev/null; then
    check "供应链 denylist" pass "clawhub/* 已封锁"
else
    check "供应链 denylist" fail "denylist 缺失或 clawhub/* 未封锁！"
fi

# G1.6 HF Token 权限
HF_ENV=~/.openclaw/workspace/.env
if [ -f "$HF_ENV" ]; then
    perm=$(stat -c %a "$HF_ENV" 2>/dev/null || echo "unknown")
    if [ "$perm" = "600" ]; then
        check "HF Token 权限" pass "600"
    else
        check "HF Token 权限" warn "权限为 $perm（应为 600）"
    fi
else
    check "HF Token 权限" warn ".env 文件不存在（无需检查）"
fi

# G1.7 requirements hash 锁
REQ_LOCK=~/.openclaw/workspace/VoxBridge/requirements.lock.txt
if [ -f "$REQ_LOCK" ]; then
    hash_count=$(grep -c "sha256:" "$REQ_LOCK" 2>/dev/null || echo 0)
    check "requirements hash 锁" pass "${hash_count} 条 sha256 记录"
else
    check "requirements hash 锁" warn "requirements.lock.txt 不存在"
fi

echo ""
echo "=== 检查结果汇总 ==="
echo "PASS: $PASS  WARN: $WARN  FAIL: $FAIL"

if [ "$FAIL" -gt 0 ]; then
    echo "状态: CRITICAL — 有 $FAIL 项严重问题，请立即处理"
    exit 2
elif [ "$WARN" -gt 0 ]; then
    echo "状态: WARNING — 有 $WARN 项需关注"
    exit 1
else
    echo "状态: OK — 所有检查通过"
    exit 0
fi

#!/bin/bash
# check_openclaw_startup.sh — 开机自检脚本
# 部署到 ~/.openclaw/workspace/tools/
# 验证龙虾三端（gateway/tailscale/feishu）是否正常运行

echo "===== OpenClaw 开机自检 $(date '+%Y-%m-%d %H:%M:%S') ====="

PASS=0
FAIL=0

check() {
    local name="$1"
    local cmd="$2"
    local expect="$3"
    result=$(eval "$cmd" 2>/dev/null)
    if echo "$result" | grep -q "$expect"; then
        echo "✅ $name: OK"
        PASS=$((PASS+1))
    else
        echo "❌ $name: FAIL (got: $result)"
        FAIL=$((FAIL+1))
    fi
}

# 1. gateway 服务
check "gateway服务" "systemctl --user is-active openclaw-gateway" "active"

# 2. gateway 进程
check "gateway进程" "pgrep -f 'openclaw-gateway' && echo running" "running"

# 3. tailscale 服务
check "tailscaled服务" "sudo systemctl is-active tailscaled" "active"

# 4. tailscale 连接
check "tailscale连通" "sudo tailscale status 2>/dev/null | grep -i 'xzy0626'" "xzy0626"

# 5. tailscale serve
check "tailscale-serve" "sudo tailscale serve status 2>/dev/null | grep '18789'" "18789"

# 6. AGENTS.md 版本标记
check "AGENTS版本标记" "head -3 ~/.openclaw/workspace/AGENTS.md | grep 'MODIFIED v4'" "MODIFIED v4"

# 7. AI_RULES.md 存在
check "AI_RULES.md" "test -f ~/.openclaw/workspace/AI_RULES.md && echo ok" "ok"

# 8. rule_sync_time.txt 存在
check "rule_sync_time" "test -f ~/.openclaw/memory/rule_sync_time.txt && echo ok" "ok"

# 9. 脱敏脚本存在
check "redact_json脚本" "test -f ~/.openclaw/workspace/tools/redact_json.py && echo ok" "ok"

# 10. loginctl linger
check "loginctl-linger" "loginctl show-user xzy0626 | grep 'Linger=yes'" "Linger=yes"

echo ""
echo "===== 自检结果：通过 $PASS / 失败 $FAIL ====="

if [ $FAIL -gt 0 ]; then
    echo "⚠️ 有 $FAIL 项检查失败，请排查后告知主人"
    exit 1
else
    echo "🎉 所有检查通过，龙虾运行正常"
    exit 0
fi

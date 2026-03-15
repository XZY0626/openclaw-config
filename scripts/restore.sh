#!/bin/bash
# ============================================================
# OpenClaw 前端自定义文件 恢复脚本
# 用途：OpenClaw升级后，自动恢复前端注入的自定义文件
# 位置：虚拟机 /home/xzy0626/.openclaw/scripts/restore.sh
# ============================================================

set -e

BACKUP_DIR="/home/xzy0626/.openclaw/backups"
OPENCLAW_UI="/usr/lib/node_modules/openclaw/dist/control-ui"
SCRIPTS_DIR="/home/xzy0626/.openclaw/scripts"

echo "=========================================="
echo "  OpenClaw 前端恢复"
echo "=========================================="

# 找到最新的备份
LATEST_BACKUP=$(ls -1d ${BACKUP_DIR}/*/ 2>/dev/null | sort -r | head -1)

if [ -z "$LATEST_BACKUP" ]; then
    echo "❌ 未找到任何备份，无法恢复"
    exit 1
fi

echo "使用备份: ${LATEST_BACKUP}"
echo "备份版本信息:"
cat "${LATEST_BACKUP}/version.txt" 2>/dev/null || echo "  无版本信息"
echo ""

# 检查OpenClaw UI目录是否存在
if [ ! -d "$OPENCLAW_UI" ]; then
    echo "❌ OpenClaw UI目录不存在: ${OPENCLAW_UI}"
    exit 1
fi

# 恢复model-selector-v2.js
echo "[1/3] 恢复模型选择器JS..."
if [ -f "${LATEST_BACKUP}/control-ui/model-selector-v2.js" ]; then
    sudo cp "${LATEST_BACKUP}/control-ui/model-selector-v2.js" "${OPENCLAW_UI}/assets/model-selector-v2.js"
    echo "  ✅ model-selector-v2.js 已恢复"
elif [ -f "${SCRIPTS_DIR}/model-selector-v2.js" ]; then
    sudo cp "${SCRIPTS_DIR}/model-selector-v2.js" "${OPENCLAW_UI}/assets/model-selector-v2.js"
    echo "  ✅ model-selector-v2.js 从scripts目录恢复"
else
    echo "  ❌ 未找到model-selector-v2.js"
fi

# 检查index.html是否已包含注入
echo "[2/3] 检查并注入index.html..."
if grep -q "model-selector-v2.js" "${OPENCLAW_UI}/index.html" 2>/dev/null; then
    echo "  ✅ index.html 已包含模型选择器引用，无需修改"
else
    echo "  注入模型选择器引用到index.html..."
    # 在</body>前插入script标签
    sudo sed -i 's|</body>|    <script src="./assets/model-selector-v2.js"></script>\n  </body>|' "${OPENCLAW_UI}/index.html"
    if grep -q "model-selector-v2.js" "${OPENCLAW_UI}/index.html"; then
        echo "  ✅ 注入成功"
    else
        echo "  ❌ 注入失败，请手动检查"
    fi
fi

# 恢复配置文件（如果被覆盖）
echo "[3/3] 检查配置文件..."
OPENCLAW_CONFIG="/home/xzy0626/.openclaw/openclaw.json"
if [ -f "$OPENCLAW_CONFIG" ]; then
    # 检查配置中是否还有models配置
    if python3 -c "import json; d=json.load(open('$OPENCLAW_CONFIG')); assert 'models' in d and 'providers' in d['models']" 2>/dev/null; then
        echo "  ✅ openclaw.json 模型配置完整"
    else
        echo "  ⚠️ openclaw.json 中模型配置丢失，从备份恢复..."
        if [ -f "${LATEST_BACKUP}/config/openclaw.json" ]; then
            cp "${LATEST_BACKUP}/config/openclaw.json" "$OPENCLAW_CONFIG"
            chmod 600 "$OPENCLAW_CONFIG"
            echo "  ✅ 配置已恢复"
        fi
    fi
fi

echo ""
echo "=========================================="
echo "  ✅ 恢复完成！请重启Gateway:"
echo "  openclaw gateway restart"
echo "=========================================="

#!/usr/bin/env bash
# sync_config_to_github.sh
# Auto-sync openclaw config changes to GitHub
# Usage: bash ~/.openclaw/scripts/sync_config_to_github.sh [commit_msg]
set -euo pipefail

OPENCLAW_DIR="/home/xzy0626/.openclaw"
REPO_DIR="/home/xzy0626/WorkBuddy/openclaw-config"
CONFIG_SRC="$OPENCLAW_DIR/openclaw.json"
CONFIG_DST="$REPO_DIR/openclaw-config/openclaw.json"
WORKSPACE_SRC="$OPENCLAW_DIR/workspace"
WORKSPACE_DST="$REPO_DIR/workspace"
SCRIPTS_SRC="$OPENCLAW_DIR/scripts"
SCRIPTS_DST="$REPO_DIR/scripts"
AGENTS_SRC="$OPENCLAW_DIR/agents"
AGENTS_DST="$REPO_DIR/agents"

COMMIT_MSG="${1:-auto: sync openclaw config $(date '+%Y-%m-%d %H:%M')}"

if [ ! -d "$REPO_DIR/.git" ]; then
    echo "[sync] ERROR: repo not found at $REPO_DIR"
    exit 1
fi

cd "$REPO_DIR"
git pull --rebase origin main --quiet || true

# Redact & copy openclaw.json
python3 - <<'PYEOF'
import json, copy, os

CONFIG_SRC = "/home/xzy0626/.openclaw/openclaw.json"
CONFIG_DST = "/home/xzy0626/WorkBuddy/openclaw-config/openclaw-config/openclaw.json"

with open(CONFIG_SRC) as f:
    data = json.load(f)

redacted = copy.deepcopy(data)

def redact_obj(obj):
    if isinstance(obj, dict):
        for k in obj:
            if k in ('apiKey', 'appSecret', 'token') and isinstance(obj[k], str) and obj[k] and obj[k] != '***':
                obj[k] = '***'
            else:
                redact_obj(obj[k])
    elif isinstance(obj, list):
        for v in obj:
            redact_obj(v)

redact_obj(redacted)
os.makedirs(os.path.dirname(CONFIG_DST), exist_ok=True)
with open(CONFIG_DST, 'w') as f:
    json.dump(redacted, f, indent=2, ensure_ascii=False)
print(f"[sync] openclaw.json redacted OK")
PYEOF

# Sync workspace - exclude large dirs, venv, compiled files, runtime state
rsync -a --delete \
    --exclude='*/venv/' \
    --exclude='*/.venv/' \
    --exclude='*/node_modules/' \
    --exclude='*/__pycache__/' \
    --exclude='*.pyc' \
    --exclude='*.db' \
    --exclude='*.db-shm' \
    --exclude='*.db-wal' \
    --exclude='round_counter.txt' \
    --exclude='*.log' \
    --exclude='*-backup-*/' \
    --exclude='*/dist/' \
    --exclude='*/build/' \
    --exclude='*.so' \
    --exclude='*.so.*' \
    --max-size=5m \
    "$WORKSPACE_SRC/" "$WORKSPACE_DST/" 2>&1 | grep -v 'skipping' || true
echo "[sync] workspace synced"

# Sync scripts
rsync -a --delete \
    --exclude='*.pyc' \
    --exclude='__pycache__' \
    "$SCRIPTS_SRC/" "$SCRIPTS_DST/"
echo "[sync] scripts synced"

# Sync agents (exclude auth-profiles.json and DBs)
if [ -d "$AGENTS_SRC" ]; then
    rsync -a --delete \
        --exclude='auth-profiles.json' \
        --exclude='*.db' \
        --exclude='*.db-shm' \
        --exclude='*.db-wal' \
        "$AGENTS_SRC/" "$AGENTS_DST/" 2>&1 | grep -v 'skipping' || true
    echo "[sync] agents synced (auth-profiles.json excluded)"
fi

# Git commit & push
cd "$REPO_DIR"
git add -A

if git diff --cached --quiet; then
    echo "[sync] Nothing changed, skip commit"
    exit 0
fi

git commit -m "$COMMIT_MSG"
git push origin main --quiet
echo "[sync] Pushed: $COMMIT_MSG"

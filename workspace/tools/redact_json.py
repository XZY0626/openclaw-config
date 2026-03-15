#!/usr/bin/env python3
# redact_json.py — openclaw.json 脱敏读取工具
# 部署路径：/tmp/redact_json.py（临时）和 ~/.openclaw/workspace/tools/redact_json.py（持久）
# 用途：读取 openclaw.json 时自动脱敏 API Key 等敏感字段

import json
import re
import sys
import os

CONFIG_PATH = os.path.expanduser('~/.openclaw/openclaw.json')

SENSITIVE_KEYS = {'apikey', 'api_key', 'token', 'secret', 'password', 'passwd', 'credential', 'auth', 'authorization'}

def redact_value(key, value):
    """根据 key 名称判断是否需要脱敏"""
    key_lower = key.lower()
    if any(s in key_lower for s in SENSITIVE_KEYS):
        if isinstance(value, str) and len(value) > 8:
            return value[:8] + '...' + value[-4:]
        return '[REDACTED]'
    return value

def redact(obj):
    if isinstance(obj, dict):
        return {k: redact_value(k, redact(v)) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [redact(i) for i in obj]
    return obj

try:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)
    redacted = redact(data)
    print(json.dumps(redacted, indent=2, ensure_ascii=False))
except FileNotFoundError:
    print(f"ERROR: {CONFIG_PATH} not found", file=sys.stderr)
    sys.exit(1)
except json.JSONDecodeError as e:
    print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
    sys.exit(1)

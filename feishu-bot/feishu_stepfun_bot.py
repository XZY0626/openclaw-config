#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人 - 安全版本
所有API Key已移除，需手动配置
"""

# ============================================================
# ⚠️  安全提醒：所有API Key需手动填入
# 不要在此文件中填写真实Key，使用环境变量或配置文件
# ============================================================

# API Key配置（用户需手动填入）
# 建议方案：
# 1. 使用环境变量：os.getenv('FEISHU_APP_SECRET')
# 2. 或配置文件：~/.config/feishu_bot/config.json

FEISHU_CONFIG = {
    "app_id": "cli_a9251e97b1399cd6",  # 可公开
    # "app_secret": "请手动填入或使用环境变量FEISHU_APP_SECRET"
}

MODEL_PROVIDERS = {
    "minimax": {
        # "api_key": "请手动填入或使用环境变量MINIMAX_API_KEY",
        "base_url": "https://api.minimaxi.chat/v1",
        "models": ["MiniMax-Text-01"]
    },
    # 其他provider配置...
}

# 实际API Key应从环境变量读取
import os
FEISHU_APP_SECRET = os.getenv("FEISHU_APP_SECRET", "")
MINIMAX_API_KEY = os.getenv("MINIMAX_API_KEY", "")

# ... 其余代码逻辑 ...

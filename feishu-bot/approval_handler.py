# -*- coding: utf-8 -*-
"""
飞书消息监听 - 模型审批处理
监听飞书机器人收到的"批准"/"拒绝"消息，自动处理待审批模型
集成到 feishu_stepfun_bot.py 的消息处理流程中
"""

import subprocess
import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_PATH = sys.executable
MONITOR_SCRIPT = os.path.join(SCRIPT_DIR, "model_monitor.py")


def handle_model_approval(text: str) -> str:
    """处理模型审批相关的消息，返回回复文本。如果不是审批消息返回None"""
    text_lower = text.strip().lower()

    if text_lower in ("批准", "approve", "同意", "确认", "通过"):
        try:
            result = subprocess.run(
                [PYTHON_PATH, MONITOR_SCRIPT, "approve"],
                capture_output=True, text=True, timeout=60,
                cwd=SCRIPT_DIR
            )
            output = result.stdout.strip()
            if "成功添加" in output or result.returncode == 0:
                return "✅ 新模型已批准并添加到OpenClaw配置中！"
            else:
                return f"处理结果：{output or '没有待审批的模型'}"
        except Exception as e:
            return f"处理审批时出错：{str(e)}"

    elif text_lower in ("拒绝", "reject", "忽略", "不要"):
        try:
            result = subprocess.run(
                [PYTHON_PATH, MONITOR_SCRIPT, "reject"],
                capture_output=True, text=True, timeout=30,
                cwd=SCRIPT_DIR
            )
            return "❌ 已忽略本次新模型更新。"
        except Exception as e:
            return f"处理拒绝时出错：{str(e)}"

    elif text_lower in ("检查模型", "check models", "模型更新"):
        try:
            result = subprocess.run(
                [PYTHON_PATH, MONITOR_SCRIPT, "check"],
                capture_output=True, text=True, timeout=120,
                cwd=SCRIPT_DIR
            )
            return "🔍 模型更新检查已完成，如有新模型会通知你。"
        except Exception as e:
            return f"检查模型时出错：{str(e)}"

    return None  # 不是审批消息

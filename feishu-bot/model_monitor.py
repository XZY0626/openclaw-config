# -*- coding: utf-8 -*-
"""
多平台AI模型更新监控服务
定时检查各平台的模型列表变化，发现新模型后通过飞书机器人通知用户
用户确认后自动写入OpenClaw配置

部署位置：宿主机 feishu_bot/model_monitor.py
运行方式：Windows计划任务，每6小时执行一次
"""

import json
import time
import hashlib
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import requests
from openai import OpenAI

# ==================== 配置 ====================
# 飞书机器人（阶跃AI助手）
FEISHU_APP_ID = "cli_a9251e97b1399cd6"
FEISHU_APP_SECRET = os.environ.get("FEISHU_APP_SECRET", "YOUR_FEISHU_APP_SECRET")

# 各平台API配置
PLATFORMS = {
    "stepfun": {
        "name": "阶跃星辰",
        "base_url": "https://api.stepfun.com/v1",
        "api_key": os.environ.get("STEPFUN_API_KEY", "YOUR_STEPFUN_API_KEY"),
    },
    "dashscope": {
        "name": "阿里云百炼",
        "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "api_key": os.environ.get("DASHSCOPE_API_KEY", "YOUR_DASHSCOPE_API_KEY"),
    },
    "siliconflow": {
        "name": "硅基流动",
        "base_url": "https://api.siliconflow.cn/v1",
        "api_key": os.environ.get("SILICONFLOW_API_KEY", "YOUR_SILICONFLOW_API_KEY"),
    },
    "openrouter": {
        "name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "api_key": os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY"),
    },
}

# 虚拟机SSH配置
VM_HOST = "192.168.1.100"
VM_USER = "xzy0626"
VM_PASS = "Xzy0626"

# 数据文件路径
SCRIPT_DIR = Path(os.path.dirname(os.path.abspath(__file__)))
KNOWN_MODELS_FILE = SCRIPT_DIR / "known_models.json"
PENDING_MODELS_FILE = SCRIPT_DIR / "pending_models.json"
LOG_FILE = SCRIPT_DIR / "model_monitor.log"

# ==================== 日志 ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler(str(LOG_FILE), encoding="utf-8"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# ==================== 飞书通知 ====================
def get_feishu_tenant_token():
    """获取飞书tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    resp = requests.post(url, json={
        "app_id": FEISHU_APP_ID,
        "app_secret": FEISHU_APP_SECRET,
    })
    data = resp.json()
    return data.get("tenant_access_token", "")


def send_feishu_notification(user_open_id, title, content):
    """通过飞书机器人发送消息"""
    token = get_feishu_tenant_token()
    if not token:
        logger.error("获取飞书token失败")
        return False

    url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=open_id"
    card = {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": title},
            "template": "blue"
        },
        "elements": [
            {"tag": "markdown", "content": content},
            {"tag": "action", "actions": [
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "✅ 批准添加"},
                    "type": "primary",
                    "value": {"action": "approve_models"}
                },
                {
                    "tag": "button",
                    "text": {"tag": "plain_text", "content": "❌ 暂不添加"},
                    "type": "danger",
                    "value": {"action": "reject_models"}
                }
            ]}
        ]
    }

    resp = requests.post(url, headers={
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }, json={
        "receive_id": user_open_id,
        "msg_type": "interactive",
        "content": json.dumps(card)
    })

    if resp.status_code == 200 and resp.json().get("code") == 0:
        logger.info(f"飞书通知发送成功: {title}")
        return True
    else:
        # 降级为纯文本消息
        text_msg = f"{title}\n\n{content}\n\n回复「批准」将新模型加入列表，回复「拒绝」忽略。"
        resp2 = requests.post(url, headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }, json={
            "receive_id": user_open_id,
            "msg_type": "text",
            "content": json.dumps({"text": text_msg})
        })
        return resp2.status_code == 200
    return False


def send_feishu_text(text):
    """发送纯文本飞书消息（广播给所有可达用户）"""
    token = get_feishu_tenant_token()
    if not token:
        return

    # 尝试通过chat列表找到可发送的目标
    url = "https://open.feishu.cn/open-apis/im/v1/chats?page_size=20"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"})
    if resp.status_code == 200:
        chats = resp.json().get("data", {}).get("items", [])
        for chat in chats:
            chat_id = chat.get("chat_id", "")
            if chat_id:
                send_url = "https://open.feishu.cn/open-apis/im/v1/messages?receive_id_type=chat_id"
                requests.post(send_url, headers={
                    "Authorization": f"Bearer {token}",
                    "Content-Type": "application/json"
                }, json={
                    "receive_id": chat_id,
                    "msg_type": "text",
                    "content": json.dumps({"text": text})
                })
                break


# ==================== 模型列表获取 ====================
def fetch_models_from_platform(platform_key, config):
    """从各平台获取模型列表"""
    models = []
    try:
        headers = {"Authorization": f"Bearer {config['api_key']}"}
        url = f"{config['base_url']}/models"
        resp = requests.get(url, headers=headers, timeout=30)

        if resp.status_code == 200:
            data = resp.json()
            model_list = data.get("data", [])
            if isinstance(model_list, list):
                for m in model_list:
                    model_id = m.get("id", "")
                    if model_id:
                        models.append({
                            "platform": platform_key,
                            "platform_name": config["name"],
                            "id": model_id,
                            "owned_by": m.get("owned_by", ""),
                            "created": m.get("created", 0),
                        })
            logger.info(f"[{config['name']}] 获取到 {len(models)} 个模型")
        else:
            logger.warning(f"[{config['name']}] API返回 {resp.status_code}")
    except Exception as e:
        logger.error(f"[{config['name']}] 获取模型列表失败: {e}")

    return models


def fetch_all_models():
    """获取所有平台的模型列表"""
    all_models = {}
    for key, config in PLATFORMS.items():
        models = fetch_models_from_platform(key, config)
        for m in models:
            full_id = f"{key}/{m['id']}"
            all_models[full_id] = m
    return all_models


# ==================== 已知模型管理 ====================
def load_known_models():
    """加载已知模型列表"""
    if KNOWN_MODELS_FILE.exists():
        with open(KNOWN_MODELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_known_models(models):
    """保存已知模型列表"""
    with open(KNOWN_MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2, ensure_ascii=False)


def load_pending_models():
    """加载待审批模型"""
    if PENDING_MODELS_FILE.exists():
        with open(PENDING_MODELS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_pending_models(models):
    """保存待审批模型"""
    with open(PENDING_MODELS_FILE, "w", encoding="utf-8") as f:
        json.dump(models, f, indent=2, ensure_ascii=False)


# ==================== 新模型写入OpenClaw ====================
def add_models_to_openclaw(new_models):
    """将新模型写入OpenClaw配置和前端JS"""
    try:
        import paramiko
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(VM_HOST, port=22, username=VM_USER, password=VM_PASS, timeout=10)

        # 读取当前配置
        stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=30)
        config = json.loads(stdout.read().decode("utf-8"))

        providers = config.get("models", {}).get("providers", {})
        added_count = 0

        for model in new_models:
            platform = model["platform"]
            model_id = model["id"]

            # 找到对应的provider
            matching_providers = [k for k in providers if platform in k.lower()]
            if not matching_providers:
                # 创建新provider
                provider_key = platform
                providers[provider_key] = {
                    "baseUrl": PLATFORMS.get(platform, {}).get("base_url", ""),
                    "apiKey": PLATFORMS.get(platform, {}).get("api_key", ""),
                    "api": "openai-completions",
                    "models": []
                }
                matching_providers = [provider_key]

            target_provider = matching_providers[0]
            existing_ids = [m["id"] for m in providers[target_provider].get("models", [])]

            if model_id not in existing_ids:
                providers[target_provider]["models"].append({
                    "id": model_id,
                    "name": f"{model_id} ({model['platform_name']})",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32000,
                    "maxTokens": 4096
                })
                added_count += 1

        if added_count > 0:
            # 写回配置
            new_config = json.dumps(config, indent=2, ensure_ascii=False)
            sftp = client.open_sftp()
            with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
                f.write(new_config)
            sftp.close()
            client.exec_command("chmod 600 /home/xzy0626/.openclaw/openclaw.json", timeout=10)

            # 重启Gateway
            client.exec_command("openclaw gateway restart", timeout=30)
            logger.info(f"已添加 {added_count} 个新模型到OpenClaw配置")

        client.close()
        return added_count
    except Exception as e:
        logger.error(f"写入OpenClaw配置失败: {e}")
        return 0


# ==================== 主流程 ====================
def check_for_new_models():
    """检查各平台是否有新模型"""
    logger.info("=" * 50)
    logger.info("开始检查模型更新...")

    known = load_known_models()
    current = fetch_all_models()

    if not current:
        logger.warning("未获取到任何模型，跳过本次检查")
        return

    # 找出新模型
    new_models = {}
    for full_id, model in current.items():
        if full_id not in known:
            new_models[full_id] = model

    if not new_models:
        logger.info("未发现新模型")
        # 更新已知列表
        save_known_models(current)
        return

    logger.info(f"发现 {len(new_models)} 个新模型！")

    # 按平台分组
    by_platform = {}
    for full_id, model in new_models.items():
        pname = model["platform_name"]
        if pname not in by_platform:
            by_platform[pname] = []
        by_platform[pname].append(model)

    # 构建通知内容
    lines = [f"**发现 {len(new_models)} 个新模型：**\n"]
    for pname, models in by_platform.items():
        lines.append(f"**{pname}** ({len(models)}个)：")
        for m in models[:10]:  # 最多显示10个
            lines.append(f"  • `{m['id']}`")
        if len(models) > 10:
            lines.append(f"  ...还有 {len(models)-10} 个")
        lines.append("")

    lines.append("回复「**批准**」将新模型加入OpenClaw，回复「**拒绝**」忽略。")
    content = "\n".join(lines)

    # 保存待审批模型
    save_pending_models(new_models)

    # 发送飞书通知
    send_feishu_text(f"🔔 AI模型更新提醒\n\n{content}")

    # 更新已知模型列表
    save_known_models(current)

    logger.info("通知已发送，等待用户审批")


def approve_pending_models():
    """批准待审批的模型"""
    pending = load_pending_models()
    if not pending:
        logger.info("没有待审批的模型")
        return 0

    models_list = list(pending.values())
    count = add_models_to_openclaw(models_list)

    if count > 0:
        # 清空待审批
        save_pending_models({})
        send_feishu_text(f"✅ 已成功添加 {count} 个新模型到OpenClaw！重启Gateway生效。")

    return count


def reject_pending_models():
    """拒绝待审批的模型"""
    pending = load_pending_models()
    count = len(pending)
    save_pending_models({})
    logger.info(f"已拒绝 {count} 个待审批模型")
    return count


# ==================== 入口 ====================
if __name__ == "__main__":
    if len(sys.argv) > 1:
        cmd = sys.argv[1]
        if cmd == "check":
            check_for_new_models()
        elif cmd == "approve":
            approve_pending_models()
        elif cmd == "reject":
            reject_pending_models()
        elif cmd == "list":
            known = load_known_models()
            print(f"已知模型数量: {len(known)}")
            for k in sorted(known.keys()):
                print(f"  {k}")
        else:
            print("用法: python model_monitor.py [check|approve|reject|list]")
    else:
        check_for_new_models()

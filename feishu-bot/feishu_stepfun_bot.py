# -*- coding: utf-8 -*-
"""
飞书机器人 - 阶跃星辰AI对话服务（长连接模式）
使用WebSocket长连接，无需公网IP和内网穿透
用户在飞书中发送消息给机器人，机器人调用阶跃星辰API生成回复
支持私聊和群聊（@机器人）
支持 /model 命令切换模型
"""

import json
import logging
import threading
from collections import defaultdict

import lark_oapi as lark
from openai import OpenAI

# 模型审批处理
try:
    from approval_handler import handle_model_approval
except ImportError:
    handle_model_approval = lambda text: None

# ==================== 配置区 ====================
# 飞书应用凭证
FEISHU_APP_ID = "cli_a9251e97b1399cd6"
FEISHU_APP_SECRET = "C9UQrugDAk89K00HP4g20fKXaZxOewxY"

# 多平台模型配置
MODELS = {
    # 阿里云百炼
    "qwen-max": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "qwen-max-latest", "name": "Qwen-Max (阿里云·旗舰)"},
    "qwen-plus": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "qwen-plus-latest", "name": "Qwen-Plus (阿里云·高性能)"},
    "qwen-turbo": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "qwen-turbo-latest", "name": "Qwen-Turbo (阿里云·快速)"},
    "deepseek-r1": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "deepseek-r1", "name": "DeepSeek-R1 (阿里云·推理)"},
    "deepseek-v3": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "deepseek-v3", "name": "DeepSeek-V3 (阿里云·通用)"},
    "qwq": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "qwq-32b", "name": "QwQ-32B (阿里云·推理)"},
    "qwen-coder": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1", "api_key": "sk-d647569dfdf14ab6b9054bce328ab352", "model": "qwen2.5-coder-32b-instruct", "name": "Qwen2.5-Coder-32B (阿里云·编程)"},
    # 阶跃星辰
    "step-2": {"base_url": "https://api.stepfun.com/v1", "api_key": "2nFoR2tH4n5R0CAe9EE8NVmMISzGjwOBznlSql7xCqwXXFfPSZeDK5yni2wIPu8l", "model": "step-2-16k", "name": "Step-2-16K (阶跃·旗舰)"},
    "step-1": {"base_url": "https://api.stepfun.com/v1", "api_key": "2nFoR2tH4n5R0CAe9EE8NVmMISzGjwOBznlSql7xCqwXXFfPSZeDK5yni2wIPu8l", "model": "step-1-8k", "name": "Step-1-8K (阶跃·通用)"},
    # 硅基流动
    "sf-deepseek-r1": {"base_url": "https://api.siliconflow.cn/v1", "api_key": "sk-oveedbamrusucbigqmtrnxkwijcrbmjoziwzxrgkxohspnft", "model": "deepseek-ai/DeepSeek-R1", "name": "DeepSeek-R1 (硅基流动)"},
    "sf-deepseek-v3": {"base_url": "https://api.siliconflow.cn/v1", "api_key": "sk-oveedbamrusucbigqmtrnxkwijcrbmjoziwzxrgkxohspnft", "model": "deepseek-ai/DeepSeek-V3", "name": "DeepSeek-V3 (硅基流动)"},
}

# 默认模型
DEFAULT_MODEL = "qwen-max"

# 对话历史配置（每个用户保留最近N轮对话）
MAX_HISTORY = 20

# ==================== 初始化 ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 飞书SDK客户端（用于主动发送/回复消息）
lark_client = lark.Client.builder() \
    .app_id(FEISHU_APP_ID) \
    .app_secret(FEISHU_APP_SECRET) \
    .log_level(lark.LogLevel.INFO) \
    .build()

# 用户对话历史 {user_id: [messages]}
conversation_history = defaultdict(list)
history_lock = threading.Lock()

# 用户当前选择的模型 {user_id: model_alias}
user_model_choice = defaultdict(lambda: DEFAULT_MODEL)
model_lock = threading.Lock()

# 已处理的消息ID集合（防止重复处理）
processed_messages = set()
processed_lock = threading.Lock()


def get_client_for_model(model_alias):
    """根据模型别名获取对应的OpenAI客户端和模型ID"""
    cfg = MODELS.get(model_alias, MODELS[DEFAULT_MODEL])
    client = OpenAI(api_key=cfg["api_key"], base_url=cfg["base_url"])
    return client, cfg["model"], cfg["name"]


def get_ai_reply(user_id: str, user_message: str) -> str:
    """调用AI API获取回复（根据用户选择的模型）"""
    with model_lock:
        model_alias = user_model_choice[user_id]

    client, model_id, model_name = get_client_for_model(model_alias)

    with history_lock:
        history = conversation_history[user_id]
        history.append({"role": "user", "content": user_message})
        if len(history) > MAX_HISTORY * 2:
            history[:] = history[-(MAX_HISTORY * 2):]

    messages = [
        {
            "role": "system",
            "content": f"你是AI助手（当前模型: {model_name}），通过飞书与用户对话。请用简洁、友好的方式回答问题。"
        }
    ] + list(history)

    try:
        response = client.chat.completions.create(
            model=model_id,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        reply = response.choices[0].message.content
        with history_lock:
            conversation_history[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"调用AI API失败 [{model_alias}]: {e}")
        return f"抱歉，模型 {model_name} 暂时不可用，请稍后再试或用 /model 切换模型。"


def handle_model_command(user_id: str, text: str) -> str:
    """处理 /model 命令"""
    parts = text.strip().split(maxsplit=1)

    # /model 不带参数 → 显示当前模型和可选列表
    if len(parts) == 1:
        with model_lock:
            current = user_model_choice[user_id]
        current_name = MODELS.get(current, {}).get("name", current)

        lines = [f"当前模型: {current_name}\n", "可选模型（发送 /model 别名 切换）:\n"]

        # 按平台分组
        groups = {}
        for alias, cfg in MODELS.items():
            name = cfg["name"]
            # 提取平台名
            if "阿里云" in name:
                g = "阿里云百炼"
            elif "阶跃" in name:
                g = "阶跃星辰"
            elif "硅基" in name:
                g = "硅基流动"
            else:
                g = "其他"
            if g not in groups:
                groups[g] = []
            marker = " ← 当前" if alias == current else ""
            groups[g].append(f"  {alias} → {name}{marker}")

        for g, items in groups.items():
            lines.append(f"\n【{g}】")
            lines.extend(items)

        return "\n".join(lines)

    # /model <alias> → 切换模型
    target = parts[1].strip().lower()
    if target not in MODELS:
        return f"未知模型: {target}\n发送 /model 查看可选模型列表。"

    with model_lock:
        user_model_choice[user_id] = target
    # 清除对话历史（切换模型后重新开始）
    with history_lock:
        conversation_history[user_id].clear()

    cfg = MODELS[target]
    return f"已切换到: {cfg['name']}\n对话记忆已清除，开始新对话！"


def send_feishu_reply(message_id: str, reply_text: str):
    """通过飞书API回复消息"""
    request = lark.im.v1.ReplyMessageRequest.builder() \
        .message_id(message_id) \
        .request_body(
            lark.im.v1.ReplyMessageRequestBody.builder()
            .content(json.dumps({"text": reply_text}))
            .msg_type("text")
            .build()
        ).build()

    response = lark_client.im.v1.message.reply(request)
    if not response.success():
        logger.error(f"回复消息失败: code={response.code}, msg={response.msg}")
    else:
        logger.info(f"回复消息成功: message_id={message_id}")


def do_p2_im_message_receive_v1(data: lark.im.v1.P2ImMessageReceiveV1) -> None:
    """处理飞书消息接收事件（v2.0）"""
    try:
        event = data.event
        message = event.message
        msg_id = message.message_id
        chat_type = message.chat_type  # "p2p" 或 "group"
        msg_type = message.message_type
        sender_id = event.sender.sender_id.open_id

        # 防止重复处理
        with processed_lock:
            if msg_id in processed_messages:
                logger.info(f"消息已处理，跳过: {msg_id}")
                return
            processed_messages.add(msg_id)
            if len(processed_messages) > 10000:
                processed_messages.clear()

        # 只处理文本消息
        if msg_type != "text":
            send_feishu_reply(msg_id, "目前只支持文本消息哦~")
            return

        # 解析消息内容
        content = json.loads(message.content)
        text = content.get("text", "").strip()

        # 群聊中需要@机器人才响应
        if chat_type == "group":
            if message.mentions:
                for mention in message.mentions:
                    text = text.replace(mention.key, "").strip()
            else:
                return

        if not text:
            send_feishu_reply(msg_id, "请输入您想问的问题~")
            return

        # 特殊指令：清除对话历史
        if text in ("/clear", "/reset", "清除记忆", "重新开始"):
            with history_lock:
                conversation_history[sender_id].clear()
            send_feishu_reply(msg_id, "对话记忆已清除，我们重新开始吧！")
            return

        # 模型切换指令
        if text.startswith("/model"):
            reply = handle_model_command(sender_id, text)
            send_feishu_reply(msg_id, reply)
            return

        # 模型审批处理
        approval_reply = handle_model_approval(text)
        if approval_reply:
            send_feishu_reply(msg_id, approval_reply)
            return

        logger.info(f"收到消息 [{chat_type}] from {sender_id}: {text}")

        # 调用AI获取回复（根据用户选择的模型）
        reply = get_ai_reply(sender_id, text)
        send_feishu_reply(msg_id, reply)

    except Exception as e:
        logger.error(f"处理消息异常: {e}", exc_info=True)


# ==================== 事件处理器 ====================
event_handler = lark.EventDispatcherHandler.builder("", "") \
    .register_p2_im_message_receive_v1(do_p2_im_message_receive_v1) \
    .build()


def main():
    """使用WebSocket长连接模式启动机器人"""
    logger.info("=" * 50)
    logger.info("  飞书机器人 - 阶跃星辰AI（长连接模式）")
    logger.info("=" * 50)
    logger.info("正在建立WebSocket长连接...")
    logger.info("无需公网IP，无需内网穿透！")
    logger.info("支持功能：私聊对话 / 群聊@机器人 / 多轮记忆")
    logger.info("发送 /clear 或 清除记忆 可重置对话")
    logger.info("=" * 50)

    cli = lark.ws.Client(
        FEISHU_APP_ID,
        FEISHU_APP_SECRET,
        event_handler=event_handler,
        log_level=lark.LogLevel.INFO
    )
    cli.start()


if __name__ == "__main__":
    main()

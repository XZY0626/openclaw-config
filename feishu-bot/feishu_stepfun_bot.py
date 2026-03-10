# -*- coding: utf-8 -*-
"""
飞书机器人 - 阶跃星辰AI对话服务（长连接模式）
使用WebSocket长连接，无需公网IP和内网穿透
用户在飞书中发送消息给机器人，机器人调用阶跃星辰API生成回复
支持私聊和群聊（@机器人）
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

# 阶跃星辰API配置
STEPFUN_API_KEY = "2nFoR2tH4n5R0CAe9EE8NVmMISzGjwOBznlSql7xCqwXXFfPSZeDK5yni2wIPu8l"
STEPFUN_BASE_URL = "https://api.stepfun.com/v1"
STEPFUN_MODEL = "step-2-16k"

# 对话历史配置（每个用户保留最近N轮对话）
MAX_HISTORY = 20

# ==================== 初始化 ====================
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger(__name__)

# 阶跃星辰客户端（兼容OpenAI SDK）
stepfun_client = OpenAI(
    api_key=STEPFUN_API_KEY,
    base_url=STEPFUN_BASE_URL,
)

# 飞书SDK客户端（用于主动发送/回复消息）
lark_client = lark.Client.builder() \
    .app_id(FEISHU_APP_ID) \
    .app_secret(FEISHU_APP_SECRET) \
    .log_level(lark.LogLevel.INFO) \
    .build()

# 用户对话历史 {user_id: [messages]}
conversation_history = defaultdict(list)
history_lock = threading.Lock()

# 已处理的消息ID集合（防止重复处理）
processed_messages = set()
processed_lock = threading.Lock()


def get_stepfun_reply(user_id: str, user_message: str) -> str:
    """调用阶跃星辰API获取AI回复"""
    with history_lock:
        history = conversation_history[user_id]
        history.append({"role": "user", "content": user_message})
        # 保留最近的对话轮次
        if len(history) > MAX_HISTORY * 2:
            history[:] = history[-(MAX_HISTORY * 2):]

    messages = [
        {
            "role": "system",
            "content": "你是阶跃星辰AI助手，通过飞书与用户对话。请用简洁、友好的方式回答问题。"
        }
    ] + list(history)

    try:
        response = stepfun_client.chat.completions.create(
            model=STEPFUN_MODEL,
            messages=messages,
            temperature=0.7,
            max_tokens=2048,
        )
        reply = response.choices[0].message.content
        with history_lock:
            conversation_history[user_id].append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        logger.error(f"调用阶跃星辰API失败: {e}")
        return f"抱歉，AI服务暂时不可用，请稍后再试。"


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

        # 模型审批处理
        approval_reply = handle_model_approval(text)
        if approval_reply:
            send_feishu_reply(msg_id, approval_reply)
            return

        logger.info(f"收到消息 [{chat_type}] from {sender_id}: {text}")

        # 调用阶跃星辰AI获取回复
        reply = get_stepfun_reply(sender_id, text)
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

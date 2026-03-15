#!/bin/bash
# heartbeat_write.sh - 心跳写入脚本，由 cron 任务触发后龙虾执行
# 路径: /home/xzy0626/.openclaw/scripts/heartbeat_write.sh

MEMORY_DIR="/home/xzy0626/.openclaw/workspace/memory"

# 1. 更新 last_heartbeat.txt
date '+%Y-%m-%d %H:%M:%S' > "$MEMORY_DIR/last_heartbeat.txt"

# 2. 递增 round_counter.txt
COUNTER_FILE="$MEMORY_DIR/round_counter.txt"
if [ -f "$COUNTER_FILE" ]; then
    current=$(cat "$COUNTER_FILE" 2>/dev/null | tr -d '[:space:]')
    if [[ "$current" =~ ^[0-9]+$ ]]; then
        echo $((current + 1)) > "$COUNTER_FILE"
    else
        echo "1" > "$COUNTER_FILE"
    fi
else
    echo "1" > "$COUNTER_FILE"
fi

# 3. 更新 rule_sync_time.txt
echo "$(date '+%Y-%m-%d %H:%M:%S') (cron-heartbeat)" > "$MEMORY_DIR/rule_sync_time.txt"

echo "heartbeat_write done: counter=$(cat $COUNTER_FILE)"

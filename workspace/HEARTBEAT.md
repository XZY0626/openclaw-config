# HEARTBEAT.md — 龙虾的定期任务

> ⚠️ 重要说明：openclaw 没有后台定时器，本文件的任务只在龙虾**收到消息被唤醒时**执行。
> 真正的定时触发由宿主机 Windows 任务计划程序（LobsterRuleSync）负责，每天 03:00 运行。

---

## 规则重读任务（每10轮对话触发）

**任务：** 重新读取并内化 `AI_RULES.md`，确认规则合规性

**触发条件：** 龙虾自行跟踪对话轮次，每满10轮后在下一次回应前执行

**执行方式：**
```
读取 ~/.openclaw/workspace/AI_RULES.md
→ 默读 L0 层全部条目
→ 回复：「✅ 已重读规则 v2.4.0-lobster，L0 安全层合规，继续。」
```

**计数器文件（沙箱内路径）：**
```bash
# ✅ 正确路径（workspace 沙箱内，龙虾可读写）
~/.openclaw/workspace/memory/round_counter.txt

# ❌ 错误路径（沙箱外，会报 Path escapes sandbox root）
~/.openclaw/memory/round_counter.txt
```

**实现方式（龙虾自跟踪）：**
```bash
# 读取当前轮次
cat ~/.openclaw/workspace/memory/round_counter.txt 2>/dev/null || echo "0"

# 每轮对话后更新
current=$(cat ~/.openclaw/workspace/memory/round_counter.txt 2>/dev/null || echo 0)
echo $((current + 1)) > ~/.openclaw/workspace/memory/round_counter.txt

# 每到10的倍数，重读规则
```

---

## 日志同步任务（每次对话结束时）

**注意：** 日志同步需要 GitHub SSH key 已配置（`~/.ssh/id_github`）且已添加到 GitHub。

读取本次会话摘要 → 写入 `~/ai-session-logs/logs/openclaw/YYYY-MM/YYYYMMDD-*.md` → git push

```bash
cd ~/ai-session-logs
mkdir -p logs/openclaw/$(date +%Y-%m)
# 写日志文件...
git add logs/openclaw/ INDEX.md
git commit -m "[$(date +%Y-%m-%d)] 操作描述"
git push
```

---

## 任务级规则触发（每次收到新任务）

每次主人发来新任务时，执行 Step 0（见 AGENTS.md）：
1. 读取 `~/.openclaw/workspace/AI_RULES.md`
2. 确认 L0 安全层合规
3. 更新 `~/.openclaw/workspace/memory/last_heartbeat.txt`
4. 然后开始执行任务

---

_本文件说明龙虾的任务触发规则。真正的定时保障由宿主机 Windows 任务计划程序提供。_

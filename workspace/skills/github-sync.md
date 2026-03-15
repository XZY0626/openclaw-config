# github-sync — GitHub 日志同步技能

## 用途

在每次对话结束时（或主人要求时），将操作日志推送到 GitHub。

---

## ⚠️ 重要：workspaceOnly 路径说明

openclaw 的 `write`/`read` 工具受 `workspaceOnly: true` 限制，路径必须在 workspace 内。
workspace 内已建立软链接，龙虾必须通过 workspace 路径来写日志。

### 正确路径格式（write_file 时必须用这个）

```
workspace/logs/openclaw/YYYY-MM/YYYYMMDD-主题.md   ✅
workspace/INDEX.md                                  ✅

~/ai-session-logs/logs/openclaw/...                ❌（被 workspaceOnly 拦截）
/home/xzy0626/ai-session-logs/...                  ❌（被 workspaceOnly 拦截）
```

---

## INDEX.md 分工规则（⚠️ 防止冲突）

WorkBuddy（宿主机侧）和龙虾（OpenClaw 侧）会同时写 INDEX.md，必须遵守分工：

1. **龙虾只追加 OpenClaw 分类行**，格式：
   ```
   | YYYY-MM-DD | OpenClaw | 操作描述 | 关键细节 |
   ```

2. **时间线表格由 WorkBuddy 统一维护**，龙虾不修改时间线部分。

3. **push 前必须先 pull --rebase**，避免冲突：
   ```bash
   cd ~/ai-session-logs
   git pull --rebase origin main  # ← 先拉，再 add/commit/push
   git add logs/openclaw/ INDEX.md
   git commit -m "描述"
   git push
   ```

---

## 日志写入流程（每次操作后执行）

### Step 1：写日志文件

```
write_file：workspace/logs/openclaw/YYYY-MM/YYYYMMDD-操作名称.md
```

内容包含：
- 执行摘要
- 操作细节
- 问题与解决
- 状态结论

### Step 2：更新 INDEX.md（只追加 OpenClaw 行）

通过 exec 追加（不用 write，避免覆盖）：
```bash
cd ~/ai-session-logs
git pull --rebase origin main
echo "| $(date +%Y-%m-%d) | OpenClaw | 操作描述 | 细节 |" >> logs/openclaw-index-append.tmp
# 手动插入到 INDEX.md 的 OpenClaw 分类下
```

或者用 write_file 整体重写 INDEX.md 前先读取最新版本：
```
read_file：workspace/INDEX.md（读最新内容）
write_file：workspace/INDEX.md（全量写入，保留所有行，只追加自己的行）
```

### Step 3：git push

```bash
cd ~/ai-session-logs
git pull --rebase origin main   # 必须先 pull
git add logs/openclaw/ INDEX.md
git commit -m "[YYYY-MM-DD] OpenClaw 操作描述"
git push
```

---

## 脱敏规则（L0.3）

推送前必须扫描：
- IP 地址：`192.168.x.x` 等内网 IP 脱敏为 `[VM_IP]`
- API Key：`sk-...` 全部替换为 `[REDACTED]`
- 密码：任何 `password=...` 替换为 `[REDACTED]`
- SSH 私钥内容：完全删除

---

## 当前关联仓库

- ai-session-logs：`git@github.com:XZY0626/ai-session-logs.git`
- VoxBridge：`git@github.com:XZY0626/VoxBridge.git`（注意：本地目录为 workspace/VoxBridge，无横杠）

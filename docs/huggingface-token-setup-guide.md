# Hugging Face Token 安全配置指南

> 为 OpenClaw 配置最小权限的 HF token，安全下载 gated 模型

---

## ⚠️ 安全警告

**Hugging Face Token 是敏感凭据，泄露会导致：**
- 他人冒用你的身份下载模型
- 如果开启写入权限，可能被恶意修改你的仓库
- 组织 token 泄露会影响整个团队

**务必遵循最小权限原则：只给必需的权限**

---

## 推荐 Token 配置（最安全的下载专用配置）

### 1. 令牌类型
**选择：细粒度（Fine-grained）**
- ✅ 可以精确控制每个权限
- ❌ 不要选经典 token（权限过大）

### 2. 权限设置（仅勾选以下必需项）

#### 用户权限 > 存储库（Repositories）
**必须开启：**
- ✅ **阅读访问所有公共封闭仓库的内容**  
  理由：pyannote/speaker-diarization-3.1 是 gated 模型，需要此权限才能下载

**可选（根据需要）：**
- ✅ **阅读访问您个人命名空间下所有仓库的内容**  
  理由：如果你自己的仓库中有需要使用的模型或数据集

**必须关闭（不要勾选）：**
- ❌ 写入对所有仓库内容/设置的权限  
  理由：OpenClaw 只需要下载，不需要修改任何仓库
- ❌ 查看你个人命名空间下所有门禁仓库的访问请求  
  理由：除非你需要管理访问请求，否则不需要

#### 其他所有权限类别
**全部关闭（不要勾选任何项）：**
- ❌ 推断（Inference）
- ❌ Webhook
- ❌ 收藏（Collections）
- ❌ 讨论与帖子
- ❌ 账单（Billing）
- ❌ 工作（Jobs）
- ❌ Org 权限

### 3. Token 命名
建议：`openclaw-download-only-20260315`
- 清晰表明用途和创建日期
- 如果泄露，你知道这个 token 的用途

### 4. 令牌创建后
**立刻复制 token 字符串**（它只显示一次），然后：

```bash
# 在 VM 上执行：
echo "YOUR_TOKEN_HERE" > ~/.huggingface/token
chmod 600 ~/.huggingface/token
```

---

## 验证 Token 是否生效

```bash
# 1. 检查 token 文件权限
ls -l ~/.huggingface/token
# 应该是：-rw------- (600)

# 2. 测试下载 gated 模型（以 pyannote 为例）
python3 -c "from huggingface_hub import snapshot_download; snapshot_download('pyannote/speaker-diarization-3.1', token='$(cat ~/.huggingface/token)')"
# 如果提示需要同意许可，先访问：https://huggingface.co/pyannote/speaker-diarization-3.1
```

---

## 在 OpenClaw 中安全使用

### 方法 A：环境变量（推荐）

在 VM 上执行：
```bash
echo 'export HF_TOKEN=$(cat ~/.huggingface/token)' >> ~/.bashrc
source ~/.bashrc
```

然后在 OpenClaw 的 skill 或 workspace 中：
```python
import os
from huggingface_hub import snapshot_download

token = os.getenv('HF_TOKEN')
if not token:
    raise ValueError("HF_TOKEN not set")

snapshot_download('pyannote/speaker-diarization-3.1', token=token)
```

### 方法 B：在 openclaw.json 中引用（需脱敏）

```json
{
  "env": {
    "HF_TOKEN": "@file:/home/xzy0626/.huggingface/token"
  }
}
```

⚠️ **千万不要在 openclaw.json 里直接写 token 字符串**

---

## Token 生命周期管理

### 定期轮换（建议每 3-6 个月）
1. 创建新 token（使用相同配置）
2. 更新 `~/.huggingface/token`
3. 在 HF 网站上删除旧 token

### 如果怀疑泄露
1. **立即在 Hugging Face 网站上删除该 token**
2. 创建新 token
3. 更新 VM 上的 token 文件
4. 检查 HF 账户的访问日志

---

## 常见问题

**Q: 为什么下载 gated 模型时需要 token？**
A: gated 模型需要用户同意许可协议，token 用于验证你的身份和授权状态。

**Q: 可以把这个 token 用在其他地方吗？**
A: 可以，只要用途是下载模型。但不要用于需要写入权限的操作。

**Q: 如何撤销 token？**
A: 登录 Hugging Face → Settings → Access Tokens → 找到 token → Revoke

---

*文档创建：2026-03-15*  
*适用于：OpenClaw VM 环境，仅下载不上传*

# v1.2.0 修复日志 - 模型调用问题排查与修复 (2026-03-10)

## 问题描述
在OpenClaw聊天界面通过模型选择器切换到阿里云百炼以外的模型（阶跃星辰、硅基流动、OpenRouter）时，提示调用失败。

## 排查过程

### 1. 日志分析
检查 `/tmp/openclaw/openclaw-2026-03-10.log`，未发现模型API调用层面的错误日志，仅有WebSocket连接认证相关的 `device-required` 警告（已在v1.1.0修复）。

### 2. API连通性测试
从虚拟机内部直接curl测试各平台API：

| 平台 | /models端点 | chat/completions | 结果 |
|------|------------|-----------------|------|
| 阿里云百炼 (DashScope) | ✅ 200 | ✅ 200 | 正常 |
| 阶跃星辰 (StepFun) | ✅ 200 | ✅ 200 | 正常 |
| 硅基流动 (SiliconFlow) | ✅ 200 | ✅ 200 | 正常 |
| OpenRouter | ✅ 200 | ❌ 401 | **API Key无效** |

### 3. OpenClaw CLI模型调用测试
```bash
# 阶跃星辰 - 成功
openclaw models set stepfun/step-2-16k
openclaw agent -m 'say hello' --session-id test  # 输出: "Hi there!"

# 硅基流动 - 成功
openclaw models set siliconflow/deepseek-ai/DeepSeek-V3
openclaw agent -m 'say hello' --session-id test  # 输出: "Hello there"

# OpenRouter - 失败
openclaw models set openrouter/openai/gpt-4o-mini
openclaw agent -m 'say hello' --session-id test  # 输出: "HTTP 401: User not found."
```

### 4. OpenRouter Key验证
```bash
curl -H "Authorization: Bearer sk-or-v1-..." https://openrouter.ai/api/v1/auth/key
# 返回: {"error":{"message":"User not found.","code":401}}
```
确认OpenRouter API Key已失效。

## 修复措施

### 已修复
1. **前端模型选择器升级到v3**：
   - OpenRouter模型标注 ⚠️ 警告，点击时提示"API Key已失效"而非直接调用失败
   - 改进 `/model` 命令发送机制，兼容Shadow DOM
   - 添加Toast提示反馈
   - 模型切换成功后显示确认提示

2. **恢复默认模型**：将默认模型恢复为 `dashscope-qwen/qwen-max-latest`

### 待用户操作
- **OpenRouter API Key需要更新**：当前Key `sk-or-v1-5d02...` 已失效（返回401 User not found），请到 https://openrouter.ai/settings/keys 重新生成Key后告知

## 各平台模型可用性汇总

| 平台 | 可用模型数 | 状态 |
|------|-----------|------|
| 阿里云百炼 | 15 | ✅ 全部可用 |
| 阶跃星辰 | 8 | ✅ 全部可用 |
| 硅基流动 | 6 | ✅ 全部可用 |
| OpenRouter | 11 | ❌ API Key失效 |

## 文件变更
- `openclaw-frontend/model-selector-v2.js` → 升级到v3逻辑
- `deploy/deploy_selector_v3.py` → 新增前端部署脚本
- `deploy/test_api_connectivity.py` → 新增API连通性测试脚本
- `deploy/test_model_call.py` → 新增模型调用测试脚本
- `deploy/check_model_errors.py` → 新增模型错误日志检查脚本

# Hugging Face Token 更换记录

**日期：** 2026-03-16  
**操作：** 更换 HF token 为只读 token  
**状态：** ⚠️ 需处理网络问题

---

## 更换详情

### 旧 Token
- **类型：** 读写权限 token
- **风险：** 权限过大，包含写入权限
- **状态：** 已删除

### 新 Token
- **类型：** 只读 token（细粒度权限）
- **权限：**
  - ✅ 读取所有公共封闭仓库（必需）
  - ✅ 读取个人命名空间仓库（可选）
  - ❌ 无写入权限（安全）
  - ❌ 无推断/Webhook/其他权限（安全）
- **Token：** `hf_uDTxhLJ...zAHs`（已脱敏）
- **存储：** `/home/xzy0626/.huggingface/token`（权限 600）

### 更换操作
```bash
# 更新 token 文件
echo "hf_uDTxhLJ...zAHs" > ~/.huggingface/token
chmod 600 ~/.huggingface/token
```

---

## 测试结果

### Token 验证
```
Token loaded: hf_uDTxhLJ...zAHs
Token valid: False
Authentication failed: [Errno 101] Network is unreachable
```

### 问题分析
**网络不可达：** Hugging Face 可能无法直接访问，需要配置：

1. **代理（推荐）**
   ```bash
   export https_proxy=http://your-proxy:port
   ```

2. **镜像源（备选）**
   ```bash
   export HF_ENDPOINT=https://hf-mirror.com
   ```

3. **Tailscale 内网穿透（长期方案）**
   在可访问 HF 的机器上部署代理，通过 Tailscale 内网访问

---

## 后续行动

### 立即需要
- [ ] 配置代理或镜像源
- [ ] 重新测试 token 和模型下载
- [ ] 验证 pyannote/speaker-diarization-3.1 是否可以重新下载

### 长期优化
- [ ] 考虑在国内服务器部署 Hugging Face 镜像缓存
- [ ] 配置自动化的模型下载和缓存管理

---

## 安全确认

✅ Token 权限已最小化（只读）  
✅ Token 存储权限正确（600）  
✅ Token 未出现在任何 GitHub 提交中  
⚠️ 网络访问需要配置

---

**相关文档：**
- `docs/huggingface-token-setup-guide.md` - HF token 安全配置指南
- `docs/project-cloud-storage-options.md` - 项目云端存储方案

**下次检查：** 网络配置完成后验证 token 有效性

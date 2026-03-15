# 项目云端存储方案

> 适用场景：VM 本地磁盘空间有限，项目完成后需要归档到云端，随时可恢复。

---

## 方案一：GitHub（代码项目首选）

**适用：** 纯代码项目、脚本、配置文件

**步骤：**
```bash
cd ~/workspace/YourProject

# 初始化 git（如果还没有）
git init
git remote add origin git@github.com:YOUR_USERNAME/YourProject.git

# 推送
git add -A
git commit -m "feat: initial commit"
git push -u origin main
```

**归档后清理本地：**
```bash
# 确认已推送后再删除
git log --oneline -5
rm -rf ~/workspace/YourProject
```

**恢复：**
```bash
git clone git@github.com:YOUR_USERNAME/YourProject.git ~/workspace/YourProject
```

**优点：** 免费、有版本历史、随时 clone 恢复  
**限制：** 单文件不超过 100MB，仓库建议不超过 1GB

---

## 方案二：打包压缩 + 对象存储（完整环境快照）

**适用：** 包含 venv、数据文件、模型等大型内容的项目

### 2a. 打包压缩
```bash
cd ~/workspace

# 打包（排除不必要的大文件）
tar -czf YourProject-archive-$(date +%Y%m%d).tar.gz \
  --exclude='YourProject/venv' \
  --exclude='YourProject/__pycache__' \
  --exclude='YourProject/.git' \
  --exclude='YourProject/node_modules' \
  YourProject/

# 查看包大小
ls -lh YourProject-archive-*.tar.gz
```

### 2b. 上传到腾讯云 COS
```bash
# 安装 coscli
wget https://github.com/tencentyun/coscli/releases/latest/download/coscli-linux -O ~/bin/coscli
chmod +x ~/bin/coscli

# 配置（需要 SecretId / SecretKey）
coscli config set --secret-id YOUR_SECRET_ID --secret-key YOUR_SECRET_KEY --region ap-shanghai

# 上传
coscli cp YourProject-archive-20260315.tar.gz cos://YOUR_BUCKET/archives/
```

### 2c. 上传到 Backblaze B2（免费 10GB）
```bash
# 安装 b2 cli
pip install b2

# 配置
b2 authorize-account YOUR_KEY_ID YOUR_APP_KEY

# 上传
b2 upload-file YOUR_BUCKET_NAME YourProject-archive-20260315.tar.gz archives/YourProject-archive-20260315.tar.gz
```

**恢复：**
```bash
# 从 COS 下载
coscli cp cos://YOUR_BUCKET/archives/YourProject-archive-20260315.tar.gz .

# 解压
tar -xzf YourProject-archive-20260315.tar.gz -C ~/workspace/
```

---

## 方案三：代码 + 大文件分离（推荐组合方案）

**适用：** 代码 + 大型数据/模型文件混合的项目

```
项目结构
├── 代码部分  →  GitHub 私有仓库
├── 模型/数据 →  对象存储（COS / B2）
└── 环境依赖  →  requirements.txt / pyproject.toml（只记录，不存文件）
```

**操作流程：**
```bash
# 1. 代码推 GitHub
git push origin main

# 2. 大文件打包上传 COS
tar -czf data-$(date +%Y%m%d).tar.gz data/ models/
coscli cp data-*.tar.gz cos://YOUR_BUCKET/YourProject/

# 3. 在 README 里记录大文件的下载地址
echo "大文件存储：cos://YOUR_BUCKET/YourProject/" >> README.md

# 4. 清理本地
rm -rf ~/workspace/YourProject
```

**恢复：**
```bash
# 克隆代码
git clone git@github.com:YOUR_USERNAME/YourProject.git

# 下载大文件
coscli cp cos://YOUR_BUCKET/YourProject/data-20260315.tar.gz .
tar -xzf data-20260315.tar.gz

# 重建 venv
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

---

## 快速决策表

| 项目类型 | 推荐方案 |
|----------|---------|
| 纯代码 / 脚本 | 方案一（GitHub） |
| 代码 + 少量数据（< 1GB） | 方案一（GitHub） |
| 代码 + 大型数据/模型 | 方案三（GitHub + COS） |
| 完整环境快照 | 方案二（打包 + COS） |
| 需要版本历史 | 方案一 或 方案三 |
| 只需要归档不需要版本 | 方案二 |

---

## VM 磁盘管理建议

```bash
# 查看各目录占用
du -sh ~/workspace/* | sort -rh | head -20

# 项目归档后清理
rm -rf ~/workspace/ProjectName

# 清理 npm / pip 缓存（释放空间）
npm cache clean --force
pip cache purge
```

---

*文档创建：2026-03-15*  
*适用环境：Ubuntu VM on VMware，磁盘扩容至 120G*

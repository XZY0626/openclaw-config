# -*- coding: utf-8 -*-
"""
部署脚本：将备份/恢复/监控脚本部署到虚拟机，并设置crontab
⚠️ 安全须知（L0.6/L0.7）：
  - 禁止在本文件中硬编码任何密码或密钥
  - 运行前请先设置环境变量：set VM_PASSWORD=你的虚拟机密码
  - 或在 .env 文件中配置（.env 已加入 .gitignore，不会上传GitHub）
"""
import paramiko
import os

host = "192.168.1.100"
user = "xzy0626"
# ⚠️ 请通过环境变量提供密码：set VM_PASSWORD=你的密码
pwd = os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE")

SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "openclaw-scripts")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

# 创建目录
client.exec_command("mkdir -p /home/xzy0626/.openclaw/scripts", timeout=10)
client.exec_command("mkdir -p /home/xzy0626/.openclaw/backups", timeout=10)

# 上传脚本
sftp = client.open_sftp()
scripts = ["backup.sh", "restore.sh", "upgrade-watch.sh"]
for script in scripts:
    local_path = os.path.join(SCRIPTS_DIR, script)
    remote_path = f"/home/xzy0626/.openclaw/scripts/{script}"
    if os.path.exists(local_path):
        with open(local_path, "r", encoding="utf-8") as f:
            content = f.read()
        with sftp.open(remote_path, "w") as rf:
            rf.write(content)
        print(f"✅ 已上传: {script}")
    else:
        print(f"⚠️ 文件不存在: {local_path}")

# 同时上传model-selector-v2.js到scripts目录作为备份源
local_js = os.path.join(os.path.dirname(os.path.abspath(__file__)), "model-selector-v2.js")
if os.path.exists(local_js):
    with open(local_js, "r", encoding="utf-8") as f:
        js_content = f.read()
    with sftp.open("/home/xzy0626/.openclaw/scripts/model-selector-v2.js", "w") as rf:
        rf.write(js_content)
    print("✅ 已上传: model-selector-v2.js (备份源)")

sftp.close()

# 设置执行权限
client.exec_command("chmod +x /home/xzy0626/.openclaw/scripts/*.sh", timeout=10)
print("✅ 已设置执行权限")

# 设置crontab - 每5分钟运行upgrade-watch
stdin, stdout, stderr = client.exec_command("crontab -l 2>/dev/null", timeout=10)
current_cron = stdout.read().decode()

cron_entry = "*/5 * * * * /home/xzy0626/.openclaw/scripts/upgrade-watch.sh >> /home/xzy0626/.openclaw/upgrade-watch.log 2>&1"

if "upgrade-watch" not in current_cron:
    new_cron = current_cron.rstrip() + "\n" + cron_entry + "\n"
    stdin, stdout, stderr = client.exec_command(f'echo "{new_cron}" | crontab -', timeout=10)
    stderr.read()
    print("✅ 已添加crontab定时任务（每5分钟检查版本变化）")
else:
    print("✅ crontab已存在upgrade-watch任务")

# 执行一次备份
stdin, stdout, stderr = client.exec_command("bash /home/xzy0626/.openclaw/scripts/backup.sh", timeout=30)
print("\n=== 首次备份 ===")
print(stdout.read().decode())

# 记录当前版本
stdin, stdout, stderr = client.exec_command("openclaw --version > /home/xzy0626/.openclaw/last_known_version.txt 2>&1", timeout=10)
print("✅ 已记录当前版本")

client.close()
print("\n✅ 虚拟机部署完成！")

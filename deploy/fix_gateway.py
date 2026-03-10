# -*- coding: utf-8 -*-
import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 读取配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=10)
config = json.loads(stdout.read().decode())

# 确保controlUi配置正确
config["gateway"]["controlUi"] = {
    "allowedOrigins": [
        "http://192.168.1.100:18789",
        "http://localhost:18789",
        "http://127.0.0.1:18789"
    ],
    "allowInsecureAuth": True,
    "dangerouslyDisableDeviceAuth": True
}

# 确保auth配置正确
config["gateway"]["auth"] = {
    "mode": "token",
    "token": "57056649c9bb83aa7eac7bbaf203b62ff728471ec009d6da"
}

# 写回
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
    f.write(json.dumps(config, indent=2, ensure_ascii=False))
sftp.close()

client.exec_command("chmod 600 /home/xzy0626/.openclaw/openclaw.json", timeout=10)
print("✅ 配置已更新")

# 重新安装并重启gateway
stdin, stdout, stderr = client.exec_command("openclaw gateway install --force 2>&1", timeout=30)
print("install:", stdout.read().decode().strip())

stdin, stdout, stderr = client.exec_command("openclaw gateway restart 2>&1", timeout=30)
print("restart:", stdout.read().decode().strip())

import time
time.sleep(5)

# 检查状态
stdin, stdout, stderr = client.exec_command("openclaw gateway status 2>&1 | head -20", timeout=15)
print("\n=== 状态 ===")
print(stdout.read().decode())

client.close()

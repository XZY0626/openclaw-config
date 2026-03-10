# -*- coding: utf-8 -*-
import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 1. Gateway状态
stdin, stdout, stderr = client.exec_command("openclaw gateway status 2>&1", timeout=15)
print("=== Gateway状态 ===")
print(stdout.read().decode())

# 2. 读取gateway配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=10)
config = json.loads(stdout.read().decode())
gw = config.get("gateway", {})
print("=== Gateway配置 ===")
print(json.dumps(gw, indent=2, ensure_ascii=False))

# 3. 查看auth token
stdin, stdout, stderr = client.exec_command("openclaw config 2>&1 | head -30", timeout=10)
print("\n=== Config输出 ===")
print(stdout.read().decode())

# 4. 查看监听端口
stdin, stdout, stderr = client.exec_command("ss -tlnp 2>&1 | grep -E '18789|18790'", timeout=10)
print("=== 监听端口 ===")
print(stdout.read().decode())

client.close()

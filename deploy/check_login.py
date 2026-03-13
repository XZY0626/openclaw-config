# -*- coding: utf-8 -*-
import paramiko
import os, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password=os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE"), timeout=10)

# 1. 查看gateway auth配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=10)
config = json.loads(stdout.read().decode())
gw = config.get("gateway", {})
auth = gw.get("auth", {})
ui = gw.get("controlUi", {})
print("=== Auth配置 ===")
print(json.dumps(auth, indent=2))
print("\n=== ControlUI配置 ===")
print(json.dumps(ui, indent=2))

# 2. 查看systemd service文件
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.config/systemd/user/openclaw-gateway.service", timeout=10)
print("\n=== Service文件 ===")
print(stdout.read().decode())

# 3. 查看最近日志中的连接/断开信息
stdin, stdout, stderr = client.exec_command("tail -100 /tmp/openclaw/openclaw-2026-03-10.log | grep -iE 'disconnect|connect|error|websocket|auth|token|reject' | tail -20", timeout=10)
print("=== 最近连接相关日志 ===")
print(stdout.read().decode())

# 4. 检查是否有浏览器桌面环境
stdin, stdout, stderr = client.exec_command("echo $DISPLAY && which firefox 2>/dev/null && which google-chrome 2>/dev/null && which chromium-browser 2>/dev/null && dpkg -l | grep -iE 'firefox|chrom' | head -5", timeout=10)
print("=== 虚拟机浏览器环境 ===")
print(stdout.read().decode())

client.close()

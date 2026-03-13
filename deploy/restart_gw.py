# -*- coding: utf-8 -*-
import paramiko
import os, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password=os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE"), timeout=10)

# gateway restart可能会阻塞，用nohup后台执行
stdin, stdout, stderr = client.exec_command("nohup openclaw gateway restart > /tmp/gw_restart.log 2>&1 &", timeout=10)
time.sleep(1)
print("已发送重启命令")

time.sleep(8)

# 检查状态
stdin, stdout, stderr = client.exec_command("cat /tmp/gw_restart.log 2>&1", timeout=10)
print("=== 重启日志 ===")
print(stdout.read().decode())

stdin, stdout, stderr = client.exec_command("openclaw gateway status 2>&1 | head -15", timeout=15)
print("=== 状态 ===")
print(stdout.read().decode())

# 检查auth配置
stdin, stdout, stderr = client.exec_command("openclaw config get gateway.auth.mode 2>&1", timeout=10)
print("=== auth.mode ===")
print(stdout.read().decode())

client.close()

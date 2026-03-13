# -*- coding: utf-8 -*-
# ⚠️ 安全须知（L0.6/L0.7）：禁止硬编码密码，请通过环境变量提供
# 运行前设置：set VM_PASSWORD=你的虚拟机密码
import paramiko
import sys
import os

host = "192.168.1.100"
user = "xzy0626"
pwd = os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE")
cmd = sys.argv[1] if len(sys.argv) > 1 else "cat ~/.openclaw/openclaw.json"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
if out:
    print(out)
if err:
    print("[STDERR]", err)
client.close()

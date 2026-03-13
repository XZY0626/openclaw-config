# -*- coding: utf-8 -*-
import paramiko
import os
import sys
import json

host = "192.168.1.100"
user = "xzy0626"
pwd = os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

# 读取配置文件中的channels部分
cmd = "python3 -c 'import json; d=json.load(open(\"/home/xzy0626/.openclaw/openclaw.json\")); print(json.dumps(d.get(\"channels\",{}), indent=2, ensure_ascii=False))'"
stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode("utf-8", errors="replace")
err = stderr.read().decode("utf-8", errors="replace")
if out:
    print("=== channels config ===")
    print(out)
if err:
    print("[STDERR]", err)

# 读取plugins部分
cmd2 = "python3 -c 'import json; d=json.load(open(\"/home/xzy0626/.openclaw/openclaw.json\")); print(json.dumps(d.get(\"plugins\",{}), indent=2, ensure_ascii=False))'"
stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
out2 = stdout.read().decode("utf-8", errors="replace")
err2 = stderr.read().decode("utf-8", errors="replace")
if out2:
    print("=== plugins config ===")
    print(out2)
if err2:
    print("[STDERR]", err2)

client.close()

# -*- coding: utf-8 -*-
import paramiko
import os
import json

host = "192.168.1.100"
user = "xzy0626"
pwd = os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE")

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

# 读取本地的exec-approvals.json
with open(r"E:\Application\StepFund\Working Directory\feishu_bot\exec-approvals.json", "r") as f:
    approvals = f.read()

# 上传到虚拟机
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/exec-approvals.json", "w") as f:
    f.write(approvals)
sftp.close()
print("exec-approvals.json 已上传")

# 验证
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/exec-approvals.json | python3 -m json.tool", timeout=10)
print(stdout.read().decode("utf-8"))

client.close()

# -*- coding: utf-8 -*-
import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password=os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE"), timeout=10)

# 搜索最近的模型调用错误
patterns = [
    "grep -iE 'stepfun|step-2|step-1' /tmp/openclaw/openclaw-2026-03-10.log | grep -iE 'error|fail|401|403|invalid|refused|timeout|ECONNREFUSED|ENOTFOUND' | tail -10",
    "grep -iE 'siliconflow|silicon' /tmp/openclaw/openclaw-2026-03-10.log | grep -iE 'error|fail|401|403|invalid|refused|timeout' | tail -10",
    "grep -iE 'openrouter' /tmp/openclaw/openclaw-2026-03-10.log | grep -iE 'error|fail|401|403|invalid|refused|timeout' | tail -10",
    "grep -iE 'model.*error|provider.*error|completion.*error|chat.*error|api.*error' /tmp/openclaw/openclaw-2026-03-10.log | tail -15",
    "grep -iE 'ECONNREFUSED|ENOTFOUND|ETIMEDOUT|fetch.*fail|network.*error|dns' /tmp/openclaw/openclaw-2026-03-10.log | tail -10",
]

for p in patterns:
    stdin, stdout, stderr = client.exec_command(p, timeout=30)
    out = stdout.read().decode()
    if out.strip():
        print(f">>> 找到匹配")
        # 提取关键信息
        for line in out.strip().split('\n'):
            # 简化JSON日志，提取关键字段
            if 'error' in line.lower() or 'fail' in line.lower() or '401' in line or '403' in line:
                # 截取关键部分
                if len(line) > 500:
                    line = line[:500] + "..."
                print(line)
        print()

client.close()

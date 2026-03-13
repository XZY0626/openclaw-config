# -*- coding: utf-8 -*-
import paramiko
import os
import sys
import time

host = "192.168.1.100"
user = "xzy0626"
pwd = os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE")

cmds = sys.argv[1:]

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

for cmd in cmds:
    print(f">>> {cmd}")
    full_cmd = f"echo '{pwd}' | sudo -S bash -c \"{cmd}\""
    stdin, stdout, stderr = client.exec_command(full_cmd, timeout=30)
    out = stdout.read().decode("utf-8", errors="replace")
    err = stderr.read().decode("utf-8", errors="replace")
    if out:
        print(out.strip())
    err_lines = [l for l in err.split('\n') if not l.startswith('[sudo]') and l.strip()]
    if err_lines:
        print("[STDERR]", '\n'.join(err_lines))
    print()
    time.sleep(1)

client.close()

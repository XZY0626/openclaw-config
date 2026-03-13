# -*- coding: utf-8 -*-
import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password=os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE"), timeout=10)

# 直接写一个干净的index.html
clean_html = """<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>OpenClaw Control</title>
    <meta name="color-scheme" content="dark light" />
    <link rel="icon" type="image/svg+xml" href="./favicon.svg" />
    <link rel="icon" type="image/png" sizes="32x32" href="./favicon-32.png" />
    <link rel="apple-touch-icon" sizes="180x180" href="./apple-touch-icon.png" />
    <script type="module" crossorigin src="./assets/index-wxM3V0HM.js"></script>
    <link rel="stylesheet" crossorigin href="./assets/index-E0j6Tkrc.css">
  </head>
  <body>
    <openclaw-app></openclaw-app>
    <script src="./assets/model-selector-v2.js"></script>
  </body>
</html>
"""

sftp = client.open_sftp()
with sftp.open("/tmp/openclaw-index-clean.html", "w") as f:
    f.write(clean_html)
sftp.close()

stdin, stdout, stderr = client.exec_command(
    "echo '{pwd}' | sudo -S cp /tmp/openclaw-index-clean.html /usr/lib/node_modules/openclaw/dist/control-ui/index.html",
    timeout=10
)
stderr.read()

# 验证
stdin, stdout, stderr = client.exec_command("cat /usr/lib/node_modules/openclaw/dist/control-ui/index.html", timeout=10)
print(stdout.read().decode())

client.close()
print("✅ 干净的index.html已写入")

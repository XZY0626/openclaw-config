# -*- coding: utf-8 -*-
import paramiko

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 1. 上传JS文件到control-ui/assets/
sftp = client.open_sftp()
with open(r"E:\Application\StepFund\Working Directory\feishu_bot\model-selector-v2.js", "r", encoding="utf-8") as f:
    js_content = f.read()

with sftp.open("/tmp/model-selector-v2.js", "w") as f:
    f.write(js_content)
sftp.close()

# sudo复制到assets目录
stdin, stdout, stderr = client.exec_command(
    "echo 'Xzy0626' | sudo -S cp /tmp/model-selector-v2.js /usr/lib/node_modules/openclaw/dist/control-ui/assets/model-selector-v2.js",
    timeout=10
)
stderr.read()

# 2. 恢复原始index.html并重新注入
stdin, stdout, stderr = client.exec_command(
    "echo 'Xzy0626' | sudo -S cp /usr/lib/node_modules/openclaw/dist/control-ui/index.html.bak /usr/lib/node_modules/openclaw/dist/control-ui/index.html",
    timeout=10
)
stderr.read()

# 3. 读取原始index.html
stdin, stdout, stderr = client.exec_command("cat /usr/lib/node_modules/openclaw/dist/control-ui/index.html", timeout=10)
original = stdout.read().decode("utf-8")

# 4. 在</body>前注入外部JS引用
new_html = original.replace(
    '</body>',
    '    <script src="./assets/model-selector-v2.js"></script>\n  </body>'
)

# 5. 写入
sftp = client.open_sftp()
with sftp.open("/tmp/openclaw-index-v2.html", "w") as f:
    f.write(new_html)
sftp.close()

stdin, stdout, stderr = client.exec_command(
    "echo 'Xzy0626' | sudo -S cp /tmp/openclaw-index-v2.html /usr/lib/node_modules/openclaw/dist/control-ui/index.html",
    timeout=10
)
stderr.read()

# 6. 验证
stdin, stdout, stderr = client.exec_command("cat /usr/lib/node_modules/openclaw/dist/control-ui/index.html", timeout=10)
html = stdout.read().decode()
print("=== index.html ===")
print(html)

stdin, stdout, stderr = client.exec_command("ls -la /usr/lib/node_modules/openclaw/dist/control-ui/assets/model-selector-v2.js", timeout=10)
print("\n=== JS文件 ===")
print(stdout.read().decode())

client.close()
print("\n✅ v2模型选择器已部署！")

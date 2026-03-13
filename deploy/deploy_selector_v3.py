# -*- coding: utf-8 -*-
"""部署更新后的前端选择器到虚拟机"""
import paramiko
import os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password=os.environ.get("VM_PASSWORD", "YOUR_VM_PASSWORD_HERE"), timeout=10)

# 上传新JS
sftp = client.open_sftp()
with open(r"E:\Application\StepFund\Working Directory\feishu_bot\model-selector-v2.js", "r", encoding="utf-8") as f:
    js = f.read()
with sftp.open("/tmp/model-selector-v2.js", "w") as f:
    f.write(js)
sftp.close()

# sudo复制到assets
stdin, stdout, stderr = client.exec_command(
    "echo '{pwd}' | sudo -S cp /tmp/model-selector-v2.js /usr/lib/node_modules/openclaw/dist/control-ui/assets/model-selector-v2.js",
    timeout=10
)
stderr.read()

# 同时更新scripts备份
client.exec_command("cp /tmp/model-selector-v2.js /home/xzy0626/.openclaw/scripts/model-selector-v2.js", timeout=10)

# 验证
stdin, stdout, stderr = client.exec_command("wc -c /usr/lib/node_modules/openclaw/dist/control-ui/assets/model-selector-v2.js", timeout=10)
print("JS文件大小:", stdout.read().decode().strip())

# 确认index.html引用存在
stdin, stdout, stderr = client.exec_command("grep 'model-selector' /usr/lib/node_modules/openclaw/dist/control-ui/index.html", timeout=10)
ref = stdout.read().decode().strip()
print("index.html引用:", ref if ref else "❌ 未找到引用")

if not ref:
    # 重新注入
    stdin, stdout, stderr = client.exec_command(
        "echo '{pwd}' | sudo -S sed -i 's|</body>|    <script src=\"./assets/model-selector-v2.js\"></script>\\n  </body>|' /usr/lib/node_modules/openclaw/dist/control-ui/index.html",
        timeout=10
    )
    print("已重新注入引用")

client.close()
print("\n✅ 前端选择器v3已部署")

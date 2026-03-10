# -*- coding: utf-8 -*-
import paramiko
import json

host = "192.168.1.100"
user = "xzy0626"
pwd = "Xzy0626"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

# 读取当前配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=30)
config_str = stdout.read().decode("utf-8", errors="replace")
config = json.loads(config_str)

# 修改channels.feishu配置
config["channels"]["feishu"] = {
    "enabled": True,
    "accounts": {
        "default": {
            "appId": "cli_a9247ccfec341cb5",
            "appSecret": "iAeWaLSaKOIjSxxTn1eg4ItOVjFuNrRW"
        }
    }
}

# 写回配置文件
new_config = json.dumps(config, indent=2, ensure_ascii=False)
# 先备份
client.exec_command("cp /home/xzy0626/.openclaw/openclaw.json /home/xzy0626/.openclaw/openclaw.json.bak.manual", timeout=10)

# 写入新配置
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
    f.write(new_config)
sftp.close()

print("配置已更新！")

# 验证
stdin, stdout, stderr = client.exec_command("python3 -c 'import json; d=json.load(open(\"/home/xzy0626/.openclaw/openclaw.json\")); print(json.dumps(d.get(\"channels\",{}), indent=2))'", timeout=30)
print("=== 更新后的channels配置 ===")
print(stdout.read().decode("utf-8"))

client.close()

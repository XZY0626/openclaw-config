# -*- coding: utf-8 -*-
import paramiko, json

host = "192.168.1.100"
user = "xzy0626"
pwd = "Xzy0626"

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect(host, port=22, username=user, password=pwd, timeout=10)

# 读取当前配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=30)
config = json.loads(stdout.read().decode("utf-8"))

# 更新API Key
providers = config.get("models", {}).get("providers", {})

if "siliconflow" in providers:
    providers["siliconflow"]["apiKey"] = "sk-oveedbamrusucbigqmtrnxkwijcrbmjoziwzxrgkxohspnft"
    print("✅ 硅基流动 API Key 已更新")

if "openrouter" in providers:
    providers["openrouter"]["apiKey"] = "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"
    print("✅ OpenRouter API Key 已更新")

# 备份并写入
client.exec_command("cp /home/xzy0626/.openclaw/openclaw.json /home/xzy0626/.openclaw/openclaw.json.bak.keys", timeout=10)

new_config = json.dumps(config, indent=2, ensure_ascii=False)
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
    f.write(new_config)
sftp.close()

# 设置权限600
client.exec_command("chmod 600 /home/xzy0626/.openclaw/openclaw.json", timeout=10)
print("✅ 配置文件权限已设为600（仅owner可读写）")

# 验证
stdin, stdout, stderr = client.exec_command("stat -c '%a %U' /home/xzy0626/.openclaw/openclaw.json", timeout=10)
print(f"   文件权限验证: {stdout.read().decode().strip()}")

client.close()

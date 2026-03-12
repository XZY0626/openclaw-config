# -*- coding: utf-8 -*-
"""更新OpenRouter API Key + 添加step-3.5-flash:free模型"""
import paramiko, json, os

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 读取配置
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=10)
config = json.loads(stdout.read().decode())

providers = config.get("models", {}).get("providers", {})

# 1. 更新OpenRouter API Key
if "openrouter" in providers:
    providers["openrouter"]["apiKey"] = os.environ.get("OPENROUTER_API_KEY", "YOUR_OPENROUTER_API_KEY")
    print("✅ OpenRouter API Key已更新")

    # 2. 添加step-3.5-flash:free模型（检查是否已存在）
    existing_ids = [m["id"] for m in providers["openrouter"].get("models", [])]
    if "stepfun/step-3.5-flash:free" not in existing_ids:
        providers["openrouter"]["models"].insert(0, {
            "id": "stepfun/step-3.5-flash:free",
            "name": "Step-3.5-Flash (免费·推理·256K)",
            "reasoning": True,
            "input": ["text"],
            "contextWindow": 256000,
            "maxTokens": 8192
        })
        print("✅ 已添加 stepfun/step-3.5-flash:free 模型")
    else:
        print("ℹ️ 模型已存在，跳过添加")

# 写回配置
client.exec_command("cp /home/xzy0626/.openclaw/openclaw.json /home/xzy0626/.openclaw/openclaw.json.bak.or", timeout=10)
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
    f.write(json.dumps(config, indent=2, ensure_ascii=False))
sftp.close()
client.exec_command("chmod 600 /home/xzy0626/.openclaw/openclaw.json", timeout=10)
print("✅ 配置文件已写入（权限600）")

# 添加别名
stdin, stdout, stderr = client.exec_command("openclaw models aliases add step-flash openrouter/stepfun/step-3.5-flash:free 2>&1", timeout=10)
print("别名:", stdout.read().decode().strip())

# 重启Gateway
stdin, stdout, stderr = client.exec_command("nohup openclaw gateway restart > /tmp/gw_restart.log 2>&1 &", timeout=10)
import time; time.sleep(6)

# 验证
stdin, stdout, stderr = client.exec_command("openclaw models list 2>&1 | grep -iE 'step-3.5|openrouter'", timeout=15)
print("\n=== 模型列表验证 ===")
print(stdout.read().decode())

client.close()

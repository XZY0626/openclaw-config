# -*- coding: utf-8 -*-
import paramiko, time

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 测试各平台模型调用
tests = [
    ("stepfun/step-2-16k", "阶跃星辰"),
    ("siliconflow/deepseek-ai/DeepSeek-V3", "硅基流动"),
    ("openrouter/openai/gpt-4o-mini", "OpenRouter"),
]

for model_id, platform in tests:
    print(f"\n=== 测试 [{platform}] {model_id} ===")
    cmd = f'echo "say hi in 3 words" | timeout 30 openclaw agent --model "{model_id}" --no-tools --max-turns 1 2>&1 | tail -20'
    stdin, stdout, stderr = client.exec_command(cmd, timeout=60)
    out = stdout.read().decode()
    err = stderr.read().decode()
    if out.strip():
        print(out.strip()[:500])
    if err.strip():
        print("[STDERR]", err.strip()[:300])
    time.sleep(2)

client.close()

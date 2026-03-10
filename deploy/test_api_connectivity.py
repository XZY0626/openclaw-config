# -*- coding: utf-8 -*-
"""测试各平台API连通性"""
import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

# 读取配置中的providers
stdin, stdout, stderr = client.exec_command("cat /home/xzy0626/.openclaw/openclaw.json", timeout=10)
config = json.loads(stdout.read().decode())
providers = config.get("models", {}).get("providers", {})

print("=== 各平台API连通性测试 ===\n")

for name, prov in providers.items():
    base_url = prov.get("baseUrl", "")
    api_key = prov.get("apiKey", "")
    models = prov.get("models", [])
    
    if not base_url or not api_key or "REPLACE" in api_key:
        print(f"[{name}] ⚠️ 跳过 - API Key未配置")
        continue
    
    # 用curl测试 /models 端点
    test_model = models[0]["id"] if models else ""
    
    # 测试1: 列出模型
    cmd1 = f'curl -s -w "\\nHTTP_CODE:%{{http_code}}" -H "Authorization: Bearer {api_key}" "{base_url}/models" 2>&1 | tail -3'
    stdin, stdout, stderr = client.exec_command(cmd1, timeout=30)
    out1 = stdout.read().decode().strip()
    
    # 测试2: 简单chat completion
    if test_model:
        payload = json.dumps({
            "model": test_model,
            "messages": [{"role": "user", "content": "hi"}],
            "max_tokens": 5
        })
        cmd2 = f"""curl -s -w "\\nHTTP_CODE:%{{http_code}}" -X POST -H "Authorization: Bearer {api_key}" -H "Content-Type: application/json" -d '{payload}' "{base_url}/chat/completions" 2>&1 | tail -5"""
        stdin, stdout, stderr = client.exec_command(cmd2, timeout=30)
        out2 = stdout.read().decode().strip()
    else:
        out2 = "无模型可测试"
    
    # 提取HTTP状态码
    http_code1 = ""
    for line in out1.split('\n'):
        if "HTTP_CODE:" in line:
            http_code1 = line.split("HTTP_CODE:")[1].strip()
    
    http_code2 = ""
    for line in out2.split('\n'):
        if "HTTP_CODE:" in line:
            http_code2 = line.split("HTTP_CODE:")[1].strip()
    
    status1 = "✅" if http_code1 == "200" else f"❌({http_code1})"
    status2 = "✅" if http_code2 == "200" else f"❌({http_code2})"
    
    print(f"[{name}]")
    print(f"  baseUrl: {base_url}")
    print(f"  /models 端点: {status1}")
    print(f"  chat/completions ({test_model}): {status2}")
    if http_code2 != "200" and out2:
        # 提取错误信息
        for line in out2.split('\n'):
            if 'error' in line.lower() or 'message' in line.lower():
                print(f"  错误详情: {line[:300]}")
    print()

client.close()

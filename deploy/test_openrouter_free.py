# -*- coding: utf-8 -*-
import paramiko, json

client = paramiko.SSHClient()
client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
client.connect("192.168.1.100", port=22, username="xzy0626", password="Xzy0626", timeout=10)

payload = json.dumps({
    "model": "stepfun/step-3.5-flash:free",
    "messages": [{"role": "user", "content": "say hi in 3 words"}],
    "max_tokens": 20
})

cmd = f"""curl -s -X POST -H 'Authorization: Bearer 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' -H 'Content-Type: application/json' -d '{payload}' 'https://openrouter.ai/api/v1/chat/completions'"""

stdin, stdout, stderr = client.exec_command(cmd, timeout=30)
out = stdout.read().decode()
print(out[:1000])
client.close()

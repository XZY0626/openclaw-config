# -*- coding: utf-8 -*-
"""
为OpenClaw配置多平台、多模型支持
覆盖：阿里云百炼(DashScope)、阶跃星辰(StepFun)、硅基流动(SiliconFlow)、OpenRouter
"""
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
config = json.loads(stdout.read().decode("utf-8"))

# ==================== 构建多平台模型配置 ====================
config["models"] = {
    "mode": "merge",
    "providers": {
        # ============ 阿里云百炼 DashScope ============
        "dashscope-qwen": {
            "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "apiKey": "sk-d647569dfdf14ab6b9054bce328ab352",
            "api": "openai-completions",
            "models": [
                {
                    "id": "qwen-max-latest",
                    "name": "Qwen-Max (阿里云·旗舰)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32000,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen-plus-latest",
                    "name": "Qwen-Plus (阿里云·高性能)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen-turbo-latest",
                    "name": "Qwen-Turbo (阿里云·快速)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 1000000,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen-long",
                    "name": "Qwen-Long (阿里云·超长文本)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 10000000,
                    "maxTokens": 6000
                },
                {
                    "id": "qwen-max-2025-01-25",
                    "name": "Qwen-Max-0125 (阿里云·稳定版)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32000,
                    "maxTokens": 8192
                }
            ]
        },
        "dashscope-qwen-coder": {
            "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "apiKey": "sk-d647569dfdf14ab6b9054bce328ab352",
            "api": "openai-completions",
            "models": [
                {
                    "id": "qwen2.5-coder-32b-instruct",
                    "name": "Qwen2.5-Coder-32B (阿里云·编程)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen2.5-coder-14b-instruct",
                    "name": "Qwen2.5-Coder-14B (阿里云·编程轻量)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                }
            ]
        },
        "dashscope-reasoning": {
            "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "apiKey": "sk-d647569dfdf14ab6b9054bce328ab352",
            "api": "openai-completions",
            "models": [
                {
                    "id": "qwq-32b",
                    "name": "QwQ-32B (阿里云·推理)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen3-235b-a22b",
                    "name": "Qwen3-235B (阿里云·最强推理)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen3-32b",
                    "name": "Qwen3-32B (阿里云·推理均衡)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                }
            ]
        },
        "dashscope-deepseek": {
            "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "apiKey": "sk-d647569dfdf14ab6b9054bce328ab352",
            "api": "openai-completions",
            "models": [
                {
                    "id": "deepseek-r1",
                    "name": "DeepSeek-R1 (阿里云·深度推理)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 65536,
                    "maxTokens": 8192
                },
                {
                    "id": "deepseek-v3",
                    "name": "DeepSeek-V3 (阿里云·通用)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 65536,
                    "maxTokens": 8192
                }
            ]
        },
        "dashscope-vision": {
            "baseUrl": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "apiKey": "sk-d647569dfdf14ab6b9054bce328ab352",
            "api": "openai-completions",
            "models": [
                {
                    "id": "qwen-vl-max-latest",
                    "name": "Qwen-VL-Max (阿里云·视觉旗舰)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 32000,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen-vl-plus-latest",
                    "name": "Qwen-VL-Plus (阿里云·视觉高性能)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 32000,
                    "maxTokens": 8192
                },
                {
                    "id": "qwen2.5-vl-72b-instruct",
                    "name": "Qwen2.5-VL-72B (阿里云·视觉大)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                }
            ]
        },
        # ============ 阶跃星辰 StepFun ============
        "stepfun": {
            "baseUrl": "https://api.stepfun.com/v1",
            "apiKey": "2nFoR2tH4n5R0CAe9EE8NVmMISzGjwOBznlSql7xCqwXXFfPSZeDK5yni2wIPu8l",
            "api": "openai-completions",
            "models": [
                {
                    "id": "step-2-16k",
                    "name": "Step-2-16K (阶跃·旗舰)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 16000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1-8k",
                    "name": "Step-1-8K (阶跃·通用)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 8000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1-32k",
                    "name": "Step-1-32K (阶跃·长文本)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1-128k",
                    "name": "Step-1-128K (阶跃·超长文本)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 128000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1-256k",
                    "name": "Step-1-256K (阶跃·极长文本)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 256000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-2-16k-exp",
                    "name": "Step-2-16K-Exp (阶跃·实验版)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 16000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1v-8k",
                    "name": "Step-1V-8K (阶跃·视觉)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 8000,
                    "maxTokens": 4096
                },
                {
                    "id": "step-1.5v-mini",
                    "name": "Step-1.5V-Mini (阶跃·视觉轻量)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 16000,
                    "maxTokens": 4096
                }
            ]
        },
        # ============ 硅基流动 SiliconFlow ============
        "siliconflow": {
            "baseUrl": "https://api.siliconflow.cn/v1",
            "apiKey": "REPLACE_WITH_YOUR_SILICONFLOW_KEY",
            "api": "openai-completions",
            "models": [
                {
                    "id": "deepseek-ai/DeepSeek-R1",
                    "name": "DeepSeek-R1 (硅基·深度推理)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 65536,
                    "maxTokens": 8192
                },
                {
                    "id": "deepseek-ai/DeepSeek-V3",
                    "name": "DeepSeek-V3 (硅基·通用)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 65536,
                    "maxTokens": 8192
                },
                {
                    "id": "Qwen/Qwen2.5-72B-Instruct",
                    "name": "Qwen2.5-72B (硅基·大模型)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32768,
                    "maxTokens": 8192
                },
                {
                    "id": "Qwen/Qwen2.5-7B-Instruct",
                    "name": "Qwen2.5-7B (硅基·免费)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32768,
                    "maxTokens": 4096
                },
                {
                    "id": "THUDM/glm-4-9b-chat",
                    "name": "GLM-4-9B (硅基·免费)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32768,
                    "maxTokens": 4096
                },
                {
                    "id": "internlm/internlm2_5-7b-chat",
                    "name": "InternLM2.5-7B (硅基·免费)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 32768,
                    "maxTokens": 4096
                }
            ]
        },
        # ============ OpenRouter (国际模型聚合) ============
        "openrouter": {
            "baseUrl": "https://openrouter.ai/api/v1",
            "apiKey": "REPLACE_WITH_YOUR_OPENROUTER_KEY",
            "api": "openai-completions",
            "models": [
                {
                    "id": "openai/gpt-4o",
                    "name": "GPT-4o (OpenRouter)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 128000,
                    "maxTokens": 16384
                },
                {
                    "id": "openai/gpt-4o-mini",
                    "name": "GPT-4o-Mini (OpenRouter·经济)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 128000,
                    "maxTokens": 16384
                },
                {
                    "id": "openai/o1",
                    "name": "O1 (OpenRouter·推理)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 200000,
                    "maxTokens": 100000
                },
                {
                    "id": "openai/o3-mini",
                    "name": "O3-Mini (OpenRouter·推理经济)",
                    "reasoning": True,
                    "input": ["text"],
                    "contextWindow": 200000,
                    "maxTokens": 100000
                },
                {
                    "id": "anthropic/claude-3.5-sonnet",
                    "name": "Claude-3.5-Sonnet (OpenRouter)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 200000,
                    "maxTokens": 8192
                },
                {
                    "id": "anthropic/claude-3-opus",
                    "name": "Claude-3-Opus (OpenRouter·旗舰)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 200000,
                    "maxTokens": 4096
                },
                {
                    "id": "anthropic/claude-3-haiku",
                    "name": "Claude-3-Haiku (OpenRouter·快速)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 200000,
                    "maxTokens": 4096
                },
                {
                    "id": "google/gemini-2.0-flash-001",
                    "name": "Gemini-2.0-Flash (OpenRouter)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 1048576,
                    "maxTokens": 8192
                },
                {
                    "id": "google/gemini-2.0-pro-exp-02-05",
                    "name": "Gemini-2.0-Pro (OpenRouter·实验)",
                    "reasoning": False,
                    "input": ["text", "image"],
                    "contextWindow": 2097152,
                    "maxTokens": 8192
                },
                {
                    "id": "meta-llama/llama-3.3-70b-instruct",
                    "name": "Llama-3.3-70B (OpenRouter)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                },
                {
                    "id": "mistralai/mistral-large-2411",
                    "name": "Mistral-Large (OpenRouter)",
                    "reasoning": False,
                    "input": ["text"],
                    "contextWindow": 131072,
                    "maxTokens": 8192
                }
            ]
        }
    }
}

# 写入配置
new_config = json.dumps(config, indent=2, ensure_ascii=False)

# 备份
client.exec_command("cp /home/xzy0626/.openclaw/openclaw.json /home/xzy0626/.openclaw/openclaw.json.bak.models", timeout=10)

# 写入
sftp = client.open_sftp()
with sftp.open("/home/xzy0626/.openclaw/openclaw.json", "w") as f:
    f.write(new_config)
sftp.close()

# 设置权限
client.exec_command("chmod 600 /home/xzy0626/.openclaw/openclaw.json", timeout=10)

print("✅ 多模型配置已写入！")

# 统计
total_models = 0
for pname, pdata in config["models"]["providers"].items():
    count = len(pdata.get("models", []))
    total_models += count
    needs_key = "需要填写API Key" if "REPLACE" in pdata.get("apiKey", "") else "已配置"
    print(f"  {pname}: {count} 个模型 ({needs_key})")
print(f"\n  总计: {total_models} 个模型")

client.close()

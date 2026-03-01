#!/usr/bin/env python3
"""测试 API 端点"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "scripts"))

import requests
import json

# API 基础 URL
BASE_URL = "http://localhost:8080"

print("🧪 测试 API 端点\n")

# 测试 1: 根路径
print("[1/3] 测试根路径...")
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"  ✓ 状态: {response.status_code}")
    print(f"  ✓ 响应: {response.json()['message']}")
except Exception as e:
    print(f"  ✗ 错误: {e}")

# 测试 2: 健康检查
print("\n[2/3] 测试健康检查...")
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"  ✓ 状态: {response.status_code}")
    data = response.json()
    print(f"  ✓ 状态: {data['status']}")
    print(f"  ✓ 版本: {data['version']}")
except Exception as e:
    print(f"  ✗ 错误: {e}")

# 测试 3: 验证论点
print("\n[3/3] 测试验证论点...")
try:
    payload = {
        "claim": "多模态 AI 将在 2025 年成为主流",
        "time_window": 7,
        "llm_model": "fast"
    }

    response = requests.post(
        f"{BASE_URL}/api/verify-claim",
        json=payload,
        timeout=30
    )

    print(f"  ✓ 状态: {response.status_code}")

    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ 结论: {data.get('verdict', 'N/A')}")
        print(f"  ✓ 置信度: {data.get('confidence', 'N/A')}%")
        print(f"  ✓ 证据数: {data['stats']['total']}")

        # 显示第一条证据
        if data.get('evidence', {}).get('supporting'):
            first = data['evidence']['supporting'][0]
            print(f"  ✓ 示例证据: {first['title'][:50]}...")
    else:
        print(f"  ✗ 错误响应: {response.text}")

except requests.exceptions.ConnectionError:
    print(f"  ✗ 无法连接到服务器")
    print(f"  💡 请先启动服务器: .venv/bin/python scripts/api_server.py")
except Exception as e:
    print(f"  ✗ 错误: {e}")

print("\n" + "="*60)
print("✅ 测试完成")
print("\n📝 启动服务器:")
print("   cd '/Users/nick/Claude Code/ai-news-radar'")
print("   .venv/bin/python scripts/api_server.py")
print("\n🌐 访问 API 文档:")
print("   http://localhost:8080/docs")

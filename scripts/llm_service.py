#!/usr/bin/env python3
"""LLM 服务模块

集成 Anthropic Claude API 进行智能分析
"""

from __future__ import annotations

import os
import json
from typing import Optional
from enum import Enum

try:
    from anthropic import Anthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False


class ModelType(Enum):
    """支持的模型类型"""
    FAST = "claude-3-5-haiku-20241022"      # 快速便宜
    STANDARD = "claude-sonnet-4-20250514"   # 标准质量（当前使用）
    SMART = "claude-sonnet-4-20250514"     # 最强模型（与 standard 相同）


class LLMService:
    """LLM 服务类"""

    def __init__(self, model: ModelType = ModelType.STANDARD):
        """
        初始化 LLM 服务

        Args:
            model: 模型类型
        """
        self.model = model
        self.client = None
        self.available = False

        # 检查 SDK 是否可用
        if not ANTHROPIC_AVAILABLE:
            print("⚠️  Anthropic SDK 未安装，使用规则引擎")
            return

        # 获取 API Key
        api_key = os.environ.get("ANTHROPIC_API_KEY")

        if not api_key:
            print("⚠️  未设置 ANTHROPIC_API_KEY 环境变量")
            print("   设置方法: export ANTHROPIC_API_KEY=your_key_here")
            return

        try:
            # 初始化客户端
            self.client = Anthropic(api_key=api_key)
            self.available = True
            print(f"✅ LLM 服务已初始化 (模型: {model.value})")
        except Exception as e:
            print(f"⚠️  LLM 初始化失败: {e}")

    def is_available(self) -> bool:
        """检查服务是否可用"""
        return self.available and self.client is not None

    def analyze_claim(
        self,
        claim_text: str,
        evidence_summary: str,
        keywords: list,
        entities: list,
    ) -> Optional[dict]:
        """
        使用 LLM 分析论点

        Args:
            claim_text: 论点文本
            evidence_summary: 证据摘要
            keywords: 关键词列表
            entities: 实体列表

        Returns:
            分析结果字典，失败返回 None
        """
        if not self.is_available():
            return None

        try:
            # 构建提示词
            prompt = self._build_prompt(
                claim_text,
                evidence_summary,
                keywords,
                entities
            )

            # 调用 Claude API
            message = self.client.messages.create(
                model=self.model.value,
                max_tokens=1024,
                temperature=0.3,  # 降低温度以获得更一致的结果
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            # 提取响应文本
            response_text = message.content[0].text

            # 解析 JSON 响应
            result = self._parse_response(response_text)

            return result

        except Exception as e:
            print(f"⚠️  LLM API 调用失败: {e}")
            return None

    def _build_prompt(
        self,
        claim_text: str,
        evidence_summary: str,
        keywords: list,
        entities: list,
    ) -> str:
        """构建提示词"""
        prompt = f"""你是一个专业的事实核查专家。请基于以下新闻证据分析给定的论点。

论点: {claim_text}

关键词: {", ".join(keywords) if keywords else "无"}
实体: {", ".join(entities) if entities else "无"}

证据信息:
{evidence_summary}

请分析:
1. 有多少证据支持这个论点？
2. 有多少证据反对这个论点？
3. 证据之间是否存在矛盾？
4. 给出你的结论（PROVE/REFUTE/INCONCLUSIVE）
5. 评估你的置信度（0-100）

请严格按照以下 JSON 格式回复（只返回 JSON，不要有其他内容）:

{{
  "verdict": "PROVE" | "REFUTE" | "INCONCLUSIVE",
  "confidence": 0-100,
  "reasoning": "详细推理过程（3-5句话，中文）",
  "supporting_evidence_count": 数字,
  "refuting_evidence_count": 数字
}}
"""
        return prompt

    def _parse_response(self, response_text: str) -> dict:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            import re

            # 查找 JSON 对象
            json_match = re.search(r'\{[^{}]*\{[^{}]*\}[^{}]*\}|\{[^{}]*\}', response_text)

            if json_match:
                json_str = json_match.group(0)
                data = json.loads(json_str)

                # 验证必需字段
                required_fields = ["verdict", "confidence", "reasoning"]
                if all(field in data for field in required_fields):
                    return data

            # 如果解析失败，返回降级结果
            return {
                "verdict": "INCONCLUSIVE",
                "confidence": 50,
                "reasoning": "LLM 响应格式解析失败，建议检查输出格式",
                "supporting_evidence_count": 0,
                "refuting_evidence_count": 0
            }

        except Exception as e:
            print(f"⚠️  解析响应失败: {e}")
            return {
                "verdict": "INCONCLUSIVE",
                "confidence": 50,
                "reasoning": f"解析错误: {str(e)}",
                "supporting_evidence_count": 0,
                "refuting_evidence_count": 0
            }


# 单例测试
if __name__ == "__main__":
    import os

    # 检查 API Key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("❌ 请设置 ANTHROPIC_API_KEY 环境变量")
        print("   export ANTHROPIC_API_KEY=your_key_here")
        exit(1)

    # 创建服务
    service = LLMService(ModelType.STANDARD)

    if not service.is_available():
        print("❌ LLM 服务不可用")
        exit(1)

    # 测试调用
    print("\n🧪 测试 LLM 分析...")

    result = service.analyze_claim(
        claim_text="GPT-5 将在 2025 年发布",
        evidence_summary="支持证据: 2条 (OpenAI 暗示进展)\n反对证据: 1条 (Sam Altman 否认时间表)",
        keywords=["GPT-5", "发布", "2025"],
        entities=["OpenAI", "GPT-5", "Sam Altman"]
    )

    if result:
        print("\n✅ 分析成功:")
        print(f"  结论: {result['verdict']}")
        print(f"  置信度: {result['confidence']}%")
        print(f"  推理: {result['reasoning']}")
    else:
        print("\n❌ 分析失败")

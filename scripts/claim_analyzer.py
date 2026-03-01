#!/usr/bin/env python3
"""AI 分析模块

使用 LLM 对证据进行推理分析
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from enum import Enum

from claim_understander import ClaimAnalysis
from evidence_retriever import Evidence, EvidenceSet


class Verdict(Enum):
    """结论类型"""
    SUPPORTED = "SUPPORTED"      # 证明
    REFUTED = "REFUTED"          # 证伪
    INCONCLUSIVE = "INCONCLUSIVE"  # 无法判断


@dataclass
class AnalysisResult:
    """分析结果"""
    verdict: Verdict
    confidence: float            # 0-100
    reasoning: str               # 推理过程
    supporting_evidence_ids: List[str]
    refuting_evidence_ids: List[str]


class ClaimAnalyzer:
    """论点分析器 - 使用 LLM 进行推理"""

    def __init__(self, model: str = "fast"):
        """
        初始化分析器

        Args:
            model: 模型选择 (fast/standard/smart)
        """
        self.model = model
        self.model_config = self._get_model_config(model)

    def _get_model_config(self, model: str) -> dict:
        """获取模型配置"""
        # 对应 cc switch 的模型
        configs = {
            "fast": {
                "name": "GPT-4o mini",
                "tool": "fast",
                "description": "成本低，速度快"
            },
            "standard": {
                "name": "GPT-4o",
                "tool": "standard",
                "description": "平衡质量和成本"
            },
            "smart": {
                "name": "Claude 3.5 Sonnet",
                "tool": "smart",
                "description": "最高质量"
            }
        }
        return configs.get(model, configs["fast"])

    def analyze(
        self,
        claim_text: str,
        evidence: EvidenceSet,
        claim_analysis: ClaimAnalysis,
    ) -> AnalysisResult:
        """
        分析论点

        Args:
            claim_text: 论点文本
            evidence: 证据集合
            claim_analysis: 论点分析结果

        Returns:
            AnalysisResult 对象
        """
        # 1. 准备提示词
        prompt = self._build_prompt(claim_text, evidence, claim_analysis)

        # 2. 调用 LLM
        llm_response = self._call_llm(prompt)

        # 3. 解析响应
        result = self._parse_response(llm_response, evidence)

        return result

    def _build_prompt(
        self,
        claim_text: str,
        evidence: EvidenceSet,
        claim_analysis: ClaimAnalysis,
    ) -> str:
        """构建 LLM 提示词"""
        # 格式化证据
        evidence_text = self._format_evidence(evidence)

        prompt = f"""你是一个专业的事实核查专家。请基于以下新闻证据分析给定的论点。

论点: {claim_text}

关键词: {", ".join(claim_analysis.keywords)}
实体: {", ".join(claim_analysis.entities)}
事件类型: {claim_analysis.event_type}

证据列表 (共{len(evidence.all)}条):

{evidence_text}

请分析:
1. 有多少证据支持这个论点？
2. 有多少证据反对这个论点？
3. 证据之间是否存在矛盾？
4. 给出你的结论（PROVE/REFUTE/INCONCLUSIVE）
5. 评估你的置信度（0-100）

请严格按照以下 JSON 格式回复:

{{
  "verdict": "PROVE" | "REFUTE" | "INCONCLUSIVE",
  "confidence": 0-100,
  "reasoning": "详细推理过程（3-5句话）",
  "supporting_evidence_count": 数字,
  "refuting_evidence_count": 数字
}}
"""
        return prompt

    def _format_evidence(self, evidence: EvidenceSet) -> str:
        """格式化证据为文本"""
        lines = []

        # 支持证据（最多5条）
        if evidence.supporting:
            lines.append("支持证据:")
            for i, e in enumerate(evidence.supporting[:5], 1):
                lines.append(f"  {i}. [{e.source}] {e.title}")
                lines.append(f"     时间: {e.published_at}")
                lines.append(f"     摘要: {e.summary[:100]}...")

        # 反对证据（最多5条）
        if evidence.refuting:
            lines.append("\n反对证据:")
            for i, e in enumerate(evidence.refuting[:5], 1):
                lines.append(f"  {i}. [{e.source}] {e.title}")
                lines.append(f"     时间: {e.published_at}")
                lines.append(f"     摘要: {e.summary[:100]}...")

        # 中性证据（最多3条）
        if evidence.neutral:
            lines.append("\n中性证据:")
            for i, e in enumerate(evidence.neutral[:3], 1):
                lines.append(f"  {i}. [{e.source}] {e.title}")

        return "\n".join(lines)

    def _call_llm(self, prompt: str) -> str:
        """调用 LLM API"""
        # MVP: 使用简单的规则判断
        # TODO: 集成实际的 LLM API（OpenAI/Claude）

        # 暂时使用规则引擎
        return self._rule_based_analysis(prompt)

    def _rule_based_analysis(self, prompt: str) -> str:
        """基于规则的分析（MVP 降级方案）"""
        # 简单的关键词分析
        prompt_lower = prompt.lower()

        # 提取支持/反对证据数量
        supporting_count = prompt.count("支持证据:")
        refuting_count = prompt.count("反对证据:")

        # 规则判断
        if refuting_count == 0 and supporting_count >= 2:
            verdict = "PROVE"
            confidence = 75
            reasoning = f"基于{supporting_count}条支持证据，且无明确反对证据，该论点具有较高的可能性。"
        elif refuting_count >= 2:
            verdict = "INCONCLUSIVE"
            confidence = 40
            reasoning = f"存在{refuting_count}条反对证据与{supporting_count}条支持证据，信息存在矛盾，需要更多信息判断。"
        elif supporting_count == 0:
            verdict = "INCONCLUSIVE"
            confidence = 30
            reasoning = "未找到足够的支持证据，无法得出明确结论。"
        else:
            verdict = "INCONCLUSIVE"
            confidence = 50
            reasoning = "证据不足，需要更多相关信息才能验证该论点。"

        return f'''{{
  "verdict": "{verdict}",
  "confidence": {confidence},
  "reasoning": "{reasoning}",
  "supporting_evidence_count": {max(1, supporting_count)},
  "refuting_evidence_count": {refuting_count}
}}'''

    def _get_fallback_response(self) -> str:
        """获取降级响应"""
        # 当 LLM 不可用时，返回简单规则判断
        return '''{
  "verdict": "INCONCLUSIVE",
  "confidence": 50,
  "reasoning": "由于 LLM 服务暂时不可用，系统基于简单的关键词匹配进行分析。建议稍后重试以获得更准确的结果。",
  "supporting_evidence_count": 0,
  "refuting_evidence_count": 0
}'''

    def _parse_response(self, response: str, evidence: EvidenceSet) -> AnalysisResult:
        """解析 LLM 响应"""
        try:
            # 尝试提取 JSON
            start = response.find("{")
            end = response.rfind("}") + 1

            if start >= 0 and end > start:
                json_str = response[start:end]
                data = json.loads(json_str)

                # 映射 verdict
                verdict_map = {
                    "PROVE": Verdict.SUPPORTED,
                    "REFUTE": Verdict.REFUTED,
                    "INCONCLUSIVE": Verdict.INCONCLUSIVE,
                }
                verdict = verdict_map.get(data.get("verdict"), Verdict.INCONCLUSIVE)

                # 收集证据 ID
                supporting_ids = [e.id for e in evidence.supporting]
                refuting_ids = [e.id for e in evidence.refuting]

                return AnalysisResult(
                    verdict=verdict,
                    confidence=float(data.get("confidence", 50)),
                    reasoning=data.get("reasoning", "无详细推理"),
                    supporting_evidence_ids=supporting_ids,
                    refuting_evidence_ids=refuting_ids,
                )

        except Exception as e:
            print(f"  ⚠️ 解析 LLM 响应失败: {e}")

        # 降级：返回默认结果
        return AnalysisResult(
            verdict=Verdict.INCONCLUSIVE,
            confidence=50.0,
            reasoning="解析失败，请检查 LLM 响应格式",
            supporting_evidence_ids=[],
            refuting_evidence_ids=[],
        )


# 测试
if __name__ == "__main__":
    from claim_understander import ClaimUnderstander

    analyzer = ClaimAnalyzer(model="fast")

    # 模拟测试
    claim = "GPT-5 将在 2025 年发布"

    understander = ClaimUnderstander()
    analysis = understander.understand(claim)

    # 创建空的证据集合用于测试
    from evidence_retriever import EvidenceSet

    mock_evidence = EvidenceSet(all=[], supporting=[], refuting=[], neutral=[])

    result = analyzer.analyze(claim, mock_evidence, analysis)

    print(f"\n分析结果:")
    print(f"结论: {result.verdict.value}")
    print(f"置信度: {result.confidence}%")
    print(f"推理: {result.reasoning}")

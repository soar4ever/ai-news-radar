#!/usr/bin/env python3
"""可信度评分模块

多维度评估证据可信度
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List

from evidence_retriever import Evidence, EvidenceSet


@dataclass
class ConfidenceBreakdown:
    """可信度细分"""
    final_score: float
    source_authority: float  # 信源权威性 0-1
    evidence_count: float    # 证据数量 0-1
    consistency: float       # 一致性 0-1
    freshness: float         # 新鲜度 0-1


class ConfidenceScorer:
    """可信度评分器"""

    # 来源类型权重
    SOURCE_WEIGHTS = {
        "official": 1.0,    # 官方: 最高权重
        "analyst": 0.8,     # 分析师: 高权重
        "media": 0.6,       # 媒体: 中等权重
        "community": 0.4,   # 社区: 低权重
        "social": 0.3,      # 社交: 较低权重
    }

    def calculate_confidence(
        self,
        evidence: EvidenceSet,
        analysis,
    ) -> ConfidenceBreakdown:
        """
        计算可信度分数

        Args:
            evidence: 证据集合
            analysis: 分析结果

        Returns:
            ConfidenceBreakdown 对象
        """
        # 1. 信源权威性
        source_authority = self._calculate_source_authority(evidence)

        # 2. 证据数量
        evidence_count = self._calculate_evidence_count(evidence)

        # 3. 一致性
        consistency = self._calculate_consistency(evidence)

        # 4. 新鲜度（暂时给满分，后续可以根据时间加权）
        freshness = 1.0

        # 加权计算
        final_score = (
            source_authority * 0.3 +
            evidence_count * 0.25 +
            consistency * 0.2 +
            freshness * 0.15
        ) * 100

        return ConfidenceBreakdown(
            final_score=min(final_score, 100),  # 限制在 0-100
            source_authority=source_authority,
            evidence_count=evidence_count,
            consistency=consistency,
            freshness=freshness,
        )

    def _calculate_source_authority(self, evidence: EvidenceSet) -> float:
        """计算信源权威性"""
        if not evidence.all:
            return 0.0

        # 计算平均权重
        total_weight = 0.0
        for e in evidence.all:
            source_type = e.source_type
            weight = self.SOURCE_WEIGHTS.get(source_type, 0.5)
            total_weight += weight

        return min(total_weight / len(evidence.all), 1.0)

    def _calculate_evidence_count(self, evidence: EvidenceSet) -> float:
        """计算证据数量分数"""
        # 基础分数：证据越多越好
        total = len(evidence.all)
        if total == 0:
            return 0.0
        elif total >= 10:
            return 1.0
        else:
            return total / 10.0

    def _calculate_consistency(self, evidence: EvidenceSet) -> float:
        """计算一致性分数"""
        total = len(evidence.all)
        if total == 0:
            return 0.0

        # 计算支持/反对比例
        supporting = len(evidence.supporting)
        refuting = len(evidence.refuting)

        # 如果双方都有证据，一致性较低
        if supporting > 0 and refuting > 0:
            # 一方占主导时一致性较高
            ratio = max(supporting, refuting) / min(supporting, refuting)
            if ratio >= 3:
                return 0.7
            else:
                return 0.4
        elif supporting > 0 or refuting > 0:
            # 单方证据，一致性高
            return 1.0
        else:
            # 全是中性证据
            return 0.6


# 测试
if __name__ == "__main__":
    from evidence_retriever import Evidence, EvidenceSet

    scorer = ConfidenceScorer()

    # 模拟证据
    evidence1 = Evidence(
        id="1",
        title="OpenAI 发布 GPT-5",
        source="OpenAI Blog",
        source_type="official",
        url="https://openai.com",
        published_at="2025-03-01T10:00:00Z",
        summary="官方发布"
    )

    evidence2 = Evidence(
        id="2",
        title="分析师预测",
        source="TechCrunch",
        source_type="media",
        url="https://techcrunch.com",
        published_at="2025-03-01T11:00:00Z",
        summary="媒体报道"
    )

    evidence_set = EvidenceSet(
        all=[evidence1, evidence2],
        supporting=[evidence1, evidence2],
        refuting=[],
        neutral=[]
    )

    breakdown = scorer.calculate_confidence(evidence_set, None)

    print(f"可信度细分:")
    print(f"  最终分数: {breakdown.final_score:.1f}%")
    print(f"  信源权威性: {breakdown.source_authority:.2f}")
    print(f"  证据数量: {breakdown.evidence_count:.2f}")
    print(f"  一致性: {breakdown.consistency:.2f}")
    print(f"  新鲜度: {breakdown.freshness:.2f}")

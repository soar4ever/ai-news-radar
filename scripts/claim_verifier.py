#!/usr/bin/env python3
"""论点验证模块 - 主控制器

基于 AI 新闻数据验证论点的智能分析系统
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# 添加项目根目录到 path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

from claim_understander import ClaimUnderstander
from evidence_retriever import EvidenceRetriever
from claim_analyzer import ClaimAnalyzer
from confidence_scorer import ConfidenceScorer

UTC = timezone.utc


def verify_claim(
    claim_text: str,
    time_window_days: int = 7,
    min_confidence: int = 0,
    use_cache: bool = True,
    llm_model: str = "fast"  # fast, standard, smart
) -> dict:
    """
    验证论点的主函数

    Args:
        claim_text: 论点文本
        time_window_days: 时间窗口（天）
        min_confidence: 最小置信度阈值
        use_cache: 是否使用缓存
        llm_model: LLM 模型选择

    Returns:
        分析结果字典
    """
    print(f"🎯 开始验证论点: {claim_text}")
    print(f"⏰ 时间窗口: {time_window_days} 天")
    print(f"🤖 LLM 模型: {llm_model}")

    # 1. 论点理解
    print("\n[1/4] 理解论点...")
    understander = ClaimUnderstander()
    claim_analysis = understander.understand(claim_text)
    print(f"  ✓ 提取关键词: {claim_analysis.keywords}")
    print(f"  ✓ 识别实体: {claim_analysis.entities}")
    print(f"  ✓ 事件类型: {claim_analysis.event_type}")

    # 2. 证据检索
    print("\n[2/4] 检索证据...")
    retriever = EvidenceRetriever()
    evidence = retriever.retrieve(
        keywords=claim_analysis.keywords,
        entities=claim_analysis.entities,
        time_window_days=time_window_days,
    )
    print(f"  ✓ 找到 {len(evidence.all)} 条相关证据")
    print(f"    - 支持: {len(evidence.supporting)}")
    print(f"    - 反对: {len(evidence.refuting)}")
    print(f"    - 中性: {len(evidence.neutral)}")

    # 3. AI 分析
    print("\n[3/4] AI 分析推理...")
    analyzer = ClaimAnalyzer(model=llm_model)
    analysis = analyzer.analyze(
        claim_text=claim_text,
        evidence=evidence,
        claim_analysis=claim_analysis,
    )
    print(f"  ✓ 结论: {analysis.verdict}")
    print(f"  ✓ 置信度: {analysis.confidence}%")

    # 4. 可信度评分
    print("\n[4/4] 计算可信度...")
    scorer = ConfidenceScorer()
    confidence_breakdown = scorer.calculate_confidence(
        evidence=evidence,
        analysis=analysis,
    )
    print(f"  ✓ 最终置信度: {confidence_breakdown.final_score}%")
    print(f"    - 信源权威性: {confidence_breakdown.source_authority:.2f}")
    print(f"    - 证据数量: {confidence_breakdown.evidence_count:.2f}")
    print(f"    - 一致性: {confidence_breakdown.consistency:.2f}")

    # 组装结果
    result = {
        "claim_text": claim_text,
        "verdict": analysis.verdict.value,  # 转换为字符串
        "confidence": confidence_breakdown.final_score,
        "reasoning": analysis.reasoning,
        "evidence": {
            "supporting": [e.to_dict() for e in evidence.supporting[:10]],
            "refuting": [e.to_dict() for e in evidence.refuting[:10]],
            "neutral": [e.to_dict() for e in evidence.neutral[:10]],
        },
        "stats": {
            "total": len(evidence.all),
            "supporting_count": len(evidence.supporting),
            "refuting_count": len(evidence.refuting),
            "neutral_count": len(evidence.neutral),
        },
        "analysis_metadata": {
            "keywords": claim_analysis.keywords,
            "entities": claim_analysis.entities,
            "event_type": claim_analysis.event_type,
            "llm_model": llm_model,
            "created_at": datetime.now(UTC).isoformat(),
        }
    }

    print("\n✅ 分析完成！")
    return result


def main():
    """命令行入口"""
    parser = argparse.ArgumentParser(
        description="论点验证 - 基于 AI 新闻的智能分析"
    )
    parser.add_argument(
        "claim",
        help="要验证的论点"
    )
    parser.add_argument(
        "--time-window",
        type=int,
        default=7,
        help="时间窗口（天），默认 7"
    )
    parser.add_argument(
        "--min-confidence",
        type=int,
        default=0,
        help="最小置信度阈值 (0-100)，默认 0"
    )
    parser.add_argument(
        "--model",
        choices=["fast", "standard", "smart"],
        default="fast",
        help="LLM 模型选择 (fast/standard/smart)，默认 fast"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="输出结果到文件"
    )

    args = parser.parse_args()

    # 执行验证
    result = verify_claim(
        claim_text=args.claim,
        time_window_days=args.time_window,
        min_confidence=args.min_confidence,
        llm_model=args.model,
    )

    # 输出结果
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False))
        print(f"\n📄 结果已保存到: {args.output}")
    else:
        print("\n" + "="*60)
        print("分析结果:")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""论点理解模块

解析用户输入的论点，提取关键信息
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import List
from collections import Counter


@dataclass
class ClaimAnalysis:
    """论点分析结果"""
    keywords: List[str]          # 关键词
    entities: List[str]          # 实体（公司、产品、人物）
    event_type: str              # 事件类型
    original_text: str           # 原始文本


class ClaimUnderstander:
    """论点理解器"""

    # 常见 AI/科技公司名
    AI_COMPANIES = {
        "openai", "anthropic", "google", "microsoft", "meta",
        "amazon", "nvidia", "amd", "intel", "apple", "tesla",
        "hugging face", "stability ai", "midjourney", "character ai"
    }

    # AI 产品/模型
    AI_PRODUCTS = {
        "gpt", "gpt-4", "gpt-5", "chatgpt", "claude", "gemini",
        "llama", "mistral", "stable diffusion", "dall-e",
        "copilot", "sora", "suno", "elevenlabs"
    }

    # 事件类型关键词
    EVENT_PATTERNS = {
        "product_release": ["发布", "推出", "上线", "launch", "release"],
        "acquisition": ["收购", "并购", "收购", "acquisition", "buy"],
        "partnership": ["合作", "伙伴", "partner", "collaborate"],
        "investment": ["投资", "融资", "investment", "funding"],
        "controversy": ["争议", "质疑", "批评", "controversy", "criticism"],
        "trend": ["趋势", "主流", "普及", "trend", "mainstream"],
    }

    def understand(self, claim_text: str) -> ClaimAnalysis:
        """
        理解论点

        Args:
            claim_text: 论点文本

        Returns:
            ClaimAnalysis 对象
        """
        # 1. 提取关键词
        keywords = self._extract_keywords(claim_text)

        # 2. 识别实体
        entities = self._extract_entities(claim_text)

        # 3. 识别事件类型
        event_type = self._detect_event_type(claim_text)

        return ClaimAnalysis(
            keywords=keywords,
            entities=entities,
            event_type=event_type,
            original_text=claim_text,
        )

    def _extract_keywords(self, text: str) -> List[str]:
        """提取关键词"""
        # 转小写
        text_lower = text.lower()

        # 分词（简单按空格和标点分割）
        words = re.findall(r'\w+', text_lower)

        # 过滤停用词
        stopwords = {
            "的", "了", "是", "在", "将", "会", "能", "可以", "这个", "那个",
            "the", "a", "an", "is", "will", "can", "to", "in", "on", "at"
        }

        # 提取有意义的词（长度>=2）
        keywords = [w for w in words if len(w) >= 2 and w not in stopwords]

        # 统计词频，取前5个
        word_freq = Counter(keywords)
        top_keywords = [w for w, _ in word_freq.most_common(5)]

        return top_keywords

    def _extract_entities(self, text: str) -> List[str]:
        """识别实体"""
        text_lower = text.lower()
        entities = []

        # 识别公司名
        for company in self.AI_COMPANIES:
            if company in text_lower:
                entities.append(company.title())

        # 识别产品名
        for product in self.AI_PRODUCTS:
            if product in text_lower:
                entities.append(product.upper())

        return list(set(entities))  # 去重

    def _detect_event_type(self, text: str) -> str:
        """检测事件类型"""
        text_lower = text.lower()

        # 检查每种事件类型
        for event_type, patterns in self.EVENT_PATTERNS.items():
            for pattern in patterns:
                if pattern in text_lower or pattern.lower() in text_lower:
                    return event_type

        # 默认类型
        return "general"


# 测试
if __name__ == "__main__":
    understander = ClaimUnderstander()

    test_claims = [
        "GPT-5 将在 2025 年发布",
        "Google 收购了 Character AI",
        "多模态 AI 将在 2025 年成为主流",
    ]

    for claim in test_claims:
        analysis = understander.understand(claim)
        print(f"\n论点: {claim}")
        print(f"关键词: {analysis.keywords}")
        print(f"实体: {analysis.entities}")
        print(f"事件类型: {analysis.event_type}")

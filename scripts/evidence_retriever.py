#!/usr/bin/env python3
"""证据检索模块

从新闻数据中检索相关证据
"""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional
from zoneinfo import ZoneInfo

UTC = timezone.utc
SH_TZ = ZoneInfo("Asia/Shanghai")


@dataclass
class Evidence:
    """证据项"""
    id: str
    title: str
    source: str
    source_type: str  # official, media, social, analyst, community
    url: str
    published_at: str
    summary: str
    relevance_score: float = 0.0

    def to_dict(self) -> dict:
        """转换为字典"""
        return {
            "id": self.id,
            "title": self.title,
            "source": self.source,
            "source_type": self.source_type,
            "url": self.url,
            "published_at": self.published_at,
            "summary": self.summary,
            "relevance_score": self.relevance_score,
        }


@dataclass
class EvidenceSet:
    """证据集合"""
    all: List[Evidence]
    supporting: List[Evidence]
    refuting: List[Evidence]
    neutral: List[Evidence]


class EvidenceRetriever:
    """证据检索器"""

    def __init__(self, data_dir: Optional[Path] = None):
        """
        初始化检索器

        Args:
            data_dir: 数据目录，默认为项目根目录下的 data/
        """
        if data_dir is None:
            data_dir = Path(__file__).parent.parent / "data"

        self.data_dir = Path(data_dir)
        self.latest_file = self.data_dir / "latest-24h.json"
        self.archive_file = self.data_dir / "archive.json"

    def retrieve(
        self,
        keywords: List[str],
        entities: List[str],
        time_window_days: int = 7,
    ) -> EvidenceSet:
        """
        检索证据

        Args:
            keywords: 关键词列表
            entities: 实体列表
            time_window_days: 时间窗口（天）

        Returns:
            EvidenceSet 对象
        """
        # 1. 加载数据
        all_news = self._load_data()

        # 2. 时间过滤
        cutoff_time = datetime.now(UTC) - timedelta(days=time_window_days)
        filtered_news = self._filter_by_time(all_news, cutoff_time)

        # 3. 相关性过滤
        relevant_news = self._filter_by_relevance(
            filtered_news,
            keywords + entities
        )

        # 4. 分类（支持/反对/中性）
        classified = self._classify_evidence(
            relevant_news,
            keywords + entities
        )

        return classified

    def _load_data(self) -> List[dict]:
        """加载新闻数据"""
        all_items = []

        # 优先加载最近24h数据
        if self.latest_file.exists():
            print(f"  加载数据: {self.latest_file.name}")
            with open(self.latest_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    all_items = data.get('items', [])
                elif isinstance(data, list):
                    all_items = data

        # 补充加载归档数据（如果需要）
        if len(all_items) == 0 and self.archive_file.exists():
            print(f"  加载数据: {self.archive_file.name}")
            with open(self.archive_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, dict):
                    all_items = data.get('items', [])
                elif isinstance(data, list):
                    all_items = data

        print(f"  ✓ 加载了 {len(all_items)} 条新闻")
        return all_items

    def _filter_by_time(self, news: List[dict], cutoff: datetime) -> List[dict]:
        """按时间过滤"""
        filtered = []
        for item in news:
            pub_time_str = item.get('published_at', item.get('time', ''))
            if not pub_time_str:
                continue

            try:
                # 解析时间
                pub_time = datetime.fromisoformat(pub_time_str.replace('Z', '+00:00'))
                if pub_time >= cutoff:
                    filtered.append(item)
            except:
                continue

        print(f"  ✓ 时间过滤后剩余 {len(filtered)} 条")
        return filtered

    def _filter_by_relevance(self, news: List[dict], terms: List[str]) -> List[dict]:
        """按相关性过滤"""
        relevant = []

        for item in news:
            title = item.get('title', '').lower()
            summary = item.get('summary', item.get('excerpt', '')).lower()

            # 计算相关性分数
            score = 0.0
            for term in terms:
                term_lower = term.lower()
                if term_lower in title:
                    score += 1.0  # 标题匹配权重高
                if term_lower in summary:
                    score += 0.5  # 摘要匹配权重低

            # 至少匹配一个词
            if score > 0:
                item['_relevance_score'] = score
                relevant.append(item)

        # 按相关性排序
        relevant.sort(key=lambda x: x.get('_relevance_score', 0), reverse=True)

        print(f"  ✓ 相关性过滤后剩余 {len(relevant)} 条")
        return relevant

    def _classify_evidence(self, news: List[dict], terms: List[str]) -> EvidenceSet:
        """分类证据"""
        supporting = []
        refuting = []
        neutral = []
        all_evidence = []

        # 简单的关键词分类
        positive_keywords = ["发布", "推出", "上线", "成功", "增长", "发布", "发布"]
        negative_keywords = ["取消", "推迟", "暂停", "否认", "失败", "问题"]

        for item in news:
            title = item.get('title', '')
            source = item.get('source', item.get('site', 'Unknown'))
            url = item.get('url', '')
            published_at = item.get('published_at', item.get('time', ''))
            summary = item.get('summary', item.get('excerpt', ''))[:200]

            # 判断来源类型
            source_type = self._classify_source(source)

            # 创建证据对象
            evidence = Evidence(
                id=self._generate_id(url),
                title=title,
                source=source,
                source_type=source_type,
                url=url,
                published_at=published_at,
                summary=summary,
                relevance_score=item.get('_relevance_score', 0.0)
            )

            # 简单分类（TODO: 改用 LLM 分类）
            title_lower = title.lower()
            if any(kw in title_lower for kw in negative_keywords):
                refuting.append(evidence)
            elif any(kw in title_lower for kw in positive_keywords):
                supporting.append(evidence)
            else:
                neutral.append(evidence)

            # 添加到全部证据列表
            all_evidence.append(evidence)

        print(f"  ✓ 分类完成: 支持 {len(supporting)} | 反对 {len(refuting)} | 中性 {len(neutral)}")

        return EvidenceSet(
            all=all_evidence,
            supporting=supporting,
            refuting=refuting,
            neutral=neutral
        )

    def _classify_source(self, source: str) -> str:
        """分类来源类型"""
        source_lower = source.lower()

        # 官方
        if any(domain in source_lower for domain in [
            "openai.com", "anthropic.com", "googleblog.com",
            "blogs.microsoft.com", "about.fb.com", "nvidia.com"
        ]):
            return "official"

        # 社交
        if any(domain in source_lower for domain in [
            "twitter.com", "x.com", "linkedin.com", "weibo.com"
        ]):
            return "social"

        # 分析师/媒体
        if any(domain in source_lower for domain in [
            "techcrunch.com", "theverge.com", "arstechnica.com",
            "wired.com", "axios.com", "information.com"
        ]):
            return "analyst"

        # 默认为媒体
        return "media"

    def _generate_id(self, url: str) -> str:
        """生成证据 ID"""
        import hashlib
        return hashlib.md5(url.encode()).hexdigest()[:12]


# 测试
if __name__ == "__main__":
    retriever = EvidenceRetriever()

    # 测试检索
    evidence = retriever.retrieve(
        keywords=["gpt", "发布", "2025"],
        entities=["openai"],
        time_window_days=7
    )

    print(f"\n检索结果:")
    print(f"总计: {len(evidence.all)}")
    print(f"支持: {len(evidence.supporting)}")
    print(f"反对: {len(evidence.refuting)}")
    print(f"中性: {len(evidence.neutral)}")

    if evidence.supporting:
        print(f"\n示例支持证据:")
        for e in evidence.supporting[:3]:
            print(f"  - {e.title}")

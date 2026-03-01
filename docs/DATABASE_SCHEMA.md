# 数据库 Schema 设计

**系统:** 论点验证模块
**数据库:** SQLite (MVP) / PostgreSQL (未来)
**版本:** v1.0
**更新:** 2025-03-01

---

## 目录
1. [概述](#概述)
2. [表结构](#表结构)
3. [索引](#索引)
4. [视图](#视图)
5. [触发器](#触发器)
6. [数据迁移](#数据迁移)

---

## 概述

### 数据库设计原则

1. **规范化:** 第三范式 (3NF)
2. **性能:** 合理的索引策略
3. **扩展性:** 预留扩展字段
4. **数据完整性:** 外键约束 + 触发器

### 命名约定

- 表名: `snake_case`，复数形式
- 字段名: `snake_case`
- 主键: `id` (UUID)
- 时间戳: `created_at`, `updated_at`
- 布尔值: `is_` 前缀

---

## 表结构

### 1. claims (论点表)

存储用户提交的论点信息。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT | PK, NOT NULL | UUID v4 |
| text | TEXT | NOT NULL | 论点原始文本 |
| keywords | TEXT | - | 关键词 JSON 数组 |
| entities | TEXT | - | 实体 JSON 数组 |
| event_type | TEXT | - | 事件类型 (product_release, partnership, etc.) |
| time_window | INTEGER | NOT NULL | 时间窗口（天数） |
| status | TEXT | NOT NULL | 状态 (pending/processing/completed/failed) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | 创建时间 |
| updated_at | TIMESTAMP | - | 更新时间 |

**SQL (SQLite):**

```sql
CREATE TABLE claims (
    id TEXT PRIMARY KEY,
    text TEXT NOT NULL CHECK(length(text) >= 5 AND length(text) <= 500),
    keywords TEXT,                  -- JSON: ["GPT-5", "发布", "2025"]
    entities TEXT,                  -- JSON: ["OpenAI", "GPT-5"]
    event_type TEXT,                -- product_release, acquisition, partnership
    time_window INTEGER NOT NULL CHECK(time_window >= 1 AND time_window <= 30),
    status TEXT NOT NULL DEFAULT 'pending' CHECK(status IN ('pending', 'processing', 'completed', 'failed')),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP
);

-- 索引
CREATE INDEX idx_claims_created_at ON claims(created_at DESC);
CREATE INDEX idx_claims_status ON claims(status);
```

---

### 2. analysis_results (分析结果表)

存储每次分析的结果。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT | PK, NOT NULL | UUID v4 |
| claim_id | TEXT | FK, NOT NULL | 关联的论点 ID |
| verdict | TEXT | NOT NULL | 结论 (SUPPORTED/REFUTED/INCONCLUSIVE) |
| confidence | REAL | NOT NULL | 置信度 (0-100) |
| reasoning | TEXT | NOT NULL | LLM 推理过程 |
| evidence_count | INTEGER | NOT NULL | 总证据数 |
| supporting_count | INTEGER | NOT NULL | 支持证据数 |
| refuting_count | INTEGER | NOT NULL | 反对证据数 |
| neutral_count | INTEGER | NOT NULL | 中性证据数 |
| llm_model | TEXT | - | 使用的 LLM 模型 |
| processing_time_ms | INTEGER | - | 处理耗时（毫秒） |
| cache_hit | BOOLEAN | DEFAULT FALSE | 是否命中缓存 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | 创建时间 |

**SQL (SQLite):**

```sql
CREATE TABLE analysis_results (
    id TEXT PRIMARY KEY,
    claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    verdict TEXT NOT NULL CHECK(verdict IN ('SUPPORTED', 'REFUTED', 'INCONCLUSIVE')),
    confidence REAL NOT NULL CHECK(confidence >= 0 AND confidence <= 100),
    reasoning TEXT NOT NULL,
    evidence_count INTEGER NOT NULL DEFAULT 0,
    supporting_count INTEGER NOT NULL DEFAULT 0,
    refuting_count INTEGER NOT NULL DEFAULT 0,
    neutral_count INTEGER NOT NULL DEFAULT 0,
    llm_model TEXT,
    processing_time_ms INTEGER,
    cache_hit BOOLEAN DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_analysis_results_claim_id ON analysis_results(claim_id);
CREATE INDEX idx_analysis_results_verdict ON analysis_results(verdict);
CREATE INDEX idx_analysis_results_confidence ON analysis_results(confidence);
CREATE INDEX idx_analysis_results_created_at ON analysis_results(created_at DESC);
```

---

### 3. evidence (证据表)

存储与论点相关的新闻证据。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| id | TEXT | PK, NOT NULL | 新闻 ID (来自原始数据) |
| title | TEXT | NOT NULL | 新闻标题 |
| source | TEXT | NOT NULL | 来源网站 |
| source_type | TEXT | NOT NULL | 来源类型 (official/media/social/analyst/community) |
| url | TEXT | NOT NULL | 新闻链接 |
| published_at | TIMESTAMP | NOT NULL | 发布时间 |
| summary | TEXT | - | 新闻摘要 |
| content_hash | TEXT | - | 内容哈希（去重） |

**SQL (SQLite):**

```sql
CREATE TABLE evidence (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    source TEXT NOT NULL,
    source_type TEXT NOT NULL CHECK(source_type IN ('official', 'media', 'social', 'analyst', 'community')),
    url TEXT NOT NULL,
    published_at TIMESTAMP NOT NULL,
    summary TEXT,
    content_hash TEXT
);

-- 索引
CREATE INDEX idx_evidence_published_at ON evidence(published_at DESC);
CREATE INDEX idx_evidence_source ON evidence(source);
CREATE INDEX idx_evidence_content_hash ON evidence(content_hash);
```

---

### 4. claim_evidence (论点-证据关联表)

多对多关联表，记录证据与论点的关系。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| claim_id | TEXT | FK, PK | 论点 ID |
| evidence_id | TEXT | FK, PK | 证据 ID |
| evidence_type | TEXT | NOT NULL | 证据类型 (supporting/refuting/neutral) |
| relevance_score | REAL | NOT NULL | 相关性分数 (0-1) |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | 创建时间 |

**SQL (SQLite):**

```sql
CREATE TABLE claim_evidence (
    claim_id TEXT NOT NULL REFERENCES claims(id) ON DELETE CASCADE,
    evidence_id TEXT NOT NULL REFERENCES evidence(id) ON DELETE CASCADE,
    evidence_type TEXT NOT NULL CHECK(evidence_type IN ('supporting', 'refuting', 'neutral')),
    relevance_score REAL NOT NULL CHECK(relevance_score >= 0 AND relevance_score <= 1),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (claim_id, evidence_id)
);

-- 索引
CREATE INDEX idx_claim_evidence_claim_id ON claim_evidence(claim_id);
CREATE INDEX idx_claim_evidence_evidence_id ON claim_evidence(evidence_id);
CREATE INDEX idx_claim_evidence_type ON claim_evidence(evidence_type);
```

---

### 5. cache (缓存表)

存储常见查询的缓存结果。

| 字段 | 类型 | 约束 | 说明 |
|------|------|------|------|
| cache_key | TEXT | PK, NOT NULL | 缓存键（论点哈希） |
| claim_text | TEXT | NOT NULL | 论点文本 |
| result_json | TEXT | NOT NULL | 分析结果 JSON |
| ttl | TIMESTAMP | NOT NULL | 过期时间 |
| hit_count | INTEGER | DEFAULT 0 | 命中次数 |
| created_at | TIMESTAMP | NOT NULL, DEFAULT NOW | 创建时间 |

**SQL (SQLite):**

```sql
CREATE TABLE cache (
    cache_key TEXT PRIMARY KEY,
    claim_text TEXT NOT NULL,
    result_json TEXT NOT NULL,
    ttl TIMESTAMP NOT NULL,
    hit_count INTEGER DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_cache_ttl ON cache(ttl);
```

---

## 索引

### 索引策略

1. **主键索引:** 自动创建
2. **外键索引:** 所有外键字段
3. **查询索引:** 常用查询字段
4. **复合索引:** 多字段组合查询

### 性能优化索引

```sql
-- 复合索引：论点 + 创建时间
CREATE INDEX idx_claims_status_created ON claims(status, created_at DESC);

-- 复合索引：论点证据查询
CREATE INDEX idx_claim_evidence_claim_type ON claim_evidence(claim_id, evidence_type);

-- 覆盖索引：历史记录查询
CREATE INDEX idx_analysis_results_cover ON analysis_results(
    claim_id, verdict, confidence, created_at
);
```

---

## 视图

### v_claim_history (论点历史视图)

简化历史记录查询。

```sql
CREATE VIEW v_claim_history AS
SELECT
    c.id,
    c.text,
    c.created_at,
    ar.verdict,
    ar.confidence,
    ar.evidence_count
FROM claims c
LEFT JOIN analysis_results ar ON c.id = ar.claim_id
WHERE c.status = 'completed'
ORDER BY c.created_at DESC;
```

### v_evidence_details (证据详情视图)

```sql
CREATE VIEW v_evidence_details AS
SELECT
    ce.claim_id,
    ce.evidence_type,
    ce.relevance_score,
    e.id,
    e.title,
    e.source,
    e.source_type,
    e.url,
    e.published_at
FROM claim_evidence ce
JOIN evidence e ON ce.evidence_id = e.id;
```

---

## 触发器

### tr_claims_updated_at (更新时间戳)

自动更新 `updated_at` 字段。

```sql
CREATE TRIGGER tr_claims_updated_at
AFTER UPDATE ON claims
FOR EACH ROW
BEGIN
    UPDATE claims SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;
```

### tr_cache_hit_count (缓存命中计数)

```sql
CREATE TRIGGER tr_cache_hit_count
AFTER UPDATE ON cache
FOR EACH ROW
WHEN NEW.hit_count > OLD.hit_count
BEGIN
    UPDATE cache SET hit_count = hit_count + 1 WHERE cache_key = NEW.cache_key;
END;
```

---

## 数据迁移

### 初始化脚本

```sql
-- 01_create_tables.sql

-- 论点表
CREATE TABLE IF NOT EXISTS claims (...);

-- 分析结果表
CREATE TABLE IF NOT EXISTS analysis_results (...);

-- 证据表
CREATE TABLE IF NOT EXISTS evidence (...);

-- 关联表
CREATE TABLE IF NOT EXISTS claim_evidence (...);

-- 缓存表
CREATE TABLE IF NOT EXISTS cache (...);

-- 索引
CREATE INDEX IF NOT EXISTS ...;

-- 触发器
CREATE TRIGGER IF NOT EXISTS ...;
```

### 版本控制

| 版本 | 文件 | 说明 |
|------|------|------|
| v1.0.0 | 001_initial.sql | 初始表结构 |
| v1.1.0 | 002_add_vector_search.sql | 添加向量检索字段 |

---

## ER 图

```
┌─────────────┐
│   claims    │
│─────────────│
│ id (PK)     │
│ text        │
│ keywords    │
│ status      │
│ created_at  │
└──────┬──────┘
       │ 1
       │
       │ N
┌──────▼─────────────────┐
│   analysis_results     │
│────────────────────────│
│ id (PK)                │
│ claim_id (FK)          │
│ verdict                │
│ confidence             │
│ reasoning              │
│ created_at             │
└────────────────────────┘

┌──────┬─────────┐
│claims│         │
└──────┬─┘       │
       │ N       │ N
       │         │
┌──────▼──────────▼───┐
│   claim_evidence     │
│──────────────────────│
│ claim_id (FK, PK)    │
│ evidence_id (FK, PK) │
│ evidence_type        │
│ relevance_score      │
└──────┬───────────────┘
       │ 1
       │
       │ N
┌──────▼──────┐
│  evidence   │
│─────────────│
│ id (PK)     │
│ title       │
│ source      │
│ url         │
│ published_at│
└─────────────┘
```

---

## 查询示例

### 查询论点及其最新分析结果

```sql
SELECT
    c.*,
    ar.verdict,
    ar.confidence,
    ar.reasoning
FROM claims c
LEFT JOIN analysis_results ar ON c.id = ar.claim_id
WHERE c.id = ?
ORDER BY ar.created_at DESC
LIMIT 1;
```

### 查询论点的所有支持证据

```sql
SELECT
    e.*,
    ce.relevance_score
FROM claim_evidence ce
JOIN evidence e ON ce.evidence_id = e.id
WHERE ce.claim_id = ?
  AND ce.evidence_type = 'supporting'
ORDER BY ce.relevance_score DESC;
```

### 统计分析

```sql
-- 结论分布
SELECT
    verdict,
    COUNT(*) as count,
    AVG(confidence) as avg_confidence
FROM analysis_results
GROUP BY verdict;

-- 每日验证次数
SELECT
    DATE(created_at) as date,
    COUNT(*) as count
FROM claims
WHERE status = 'completed'
GROUP BY DATE(created_at)
ORDER BY date DESC;
```

---

## 维护

### 清理过期缓存

```sql
DELETE FROM cache WHERE ttl < CURRENT_TIMESTAMP;
```

### 清理旧数据

```sql
-- 删除 30 天前的记录
DELETE FROM claims
WHERE created_at < datetime('now', '-30 days');
```

### 数据库优化

```sql
VACUUM;  -- 重建数据库，回收空间
ANALYZE; -- 更新统计信息
```

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-03-01 | 初始版本 |

---

*本文档是 CLAIM_VERIFICATION_REQUIREMENTS.md 的配套技术规范*

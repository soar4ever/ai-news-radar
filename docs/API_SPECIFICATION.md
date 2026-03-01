# 论点验证 API 技术规范

**版本:** v1.0
**更新:** 2025-03-01

---

## 目录
1. [概述](#概述)
2. [认证](#认证)
3. [端点详情](#端点详情)
4. [数据模型](#数据模型)
5. [错误处理](#错误处理)
6. [速率限制](#速率限制)
7. [示例代码](#示例代码)

---

## 概述

**Base URL:** `http://localhost:8080/api` (开发环境)

**Content-Type:** `application/json`

**API 版本:** v1

---

## 认证

**MVP:** 无需认证（本地使用）

**未来:** API Key 或 JWT Token

```
Authorization: Bearer <token>
```

---

## 端点详情

### 1. 验证论点

验证用户提交的论点，返回分析结果。

**端点:** `POST /verify-claim`

**请求参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| claim | string | 是 | - | 待验证的论点文本 |
| time_window | integer | 否 | 7 | 时间窗口（天），范围: 1-30 |
| min_confidence | integer | 否 | 0 | 最小置信度阈值 (0-100) |
| use_vector_search | boolean | 否 | false | 是否使用向量检索（Phase 2） |

**请求示例:**

```bash
curl -X POST http://localhost:8080/api/verify-claim \
  -H "Content-Type: application/json" \
  -d '{
    "claim": "GPT-5 将在 2025 年发布",
    "time_window": 7,
    "min_confidence": 50
  }'
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "claim_id": "550e8400-e29b-41d4-a716-446655440000",
    "claim_text": "GPT-5 将在 2025 年发布",
    "verdict": "INCONCLUSIVE",
    "verdict_display": "无法判断",
    "confidence": 35,
    "confidence_level": "LOW",
    "reasoning": "基于最近7天的分析，OpenAI 官方博客暗示了 GPT-5 的进展，但 Sam Altman 在 Twitter 否认了具体的时间表。信息存在矛盾，无法确定。",
    "evidence_summary": {
      "total": 18,
      "supporting": 2,
      "refuting": 1,
      "neutral": 15
    },
    "supporting_evidence": [
      {
        "id": "news-2025-02-28-001",
        "title": "OpenAI 暗示 GPT-5 取得重大进展",
        "source": "OpenAI Blog",
        "source_type": "official",
        "url": "https://openai.com/blog/gpt5-progress",
        "published_at": "2025-02-28T10:00:00Z",
        "published_at_display": "02-28 10:00",
        "summary": "OpenAI 在官方博客中提到...",
        "relevance_score": 0.92,
        "key_points": [
          "模型性能提升",
          "安全测试进行中"
        ]
      }
    ],
    "refuting_evidence": [
      {
        "id": "news-2025-02-27-002",
        "title": "Sam Altman: 没有具体的发布时间表",
        "source": "Twitter",
        "source_type": "social",
        "url": "https://twitter.com/sama/status/123456",
        "published_at": "2025-02-27T15:30:00Z",
        "published_at_display": "02-27 15:30",
        "summary": "OpenAI CEO Sam Altman 回复网友...",
        "relevance_score": 0.88,
        "key_points": [
          "开发仍在进行",
          "不确定发布日期"
        ]
      }
    ],
    "neutral_evidence": [],
    "analysis_metadata": {
      "keywords_extracted": ["GPT-5", "发布", "2025"],
      "entities_detected": ["OpenAI", "GPT-5", "Sam Altman"],
      "event_type": "product_release",
      "time_range_start": "2025-02-21T00:00:00Z",
      "time_range_end": "2025-02-28T23:59:59Z",
      "llm_model": "gpt-4o-mini",
      "processing_time_ms": 3247,
      "cache_hit": false
    },
    "created_at": "2025-03-01T12:00:00Z"
  }
}
```

---

### 2. 获取历史记录

获取用户的验证历史。

**端点:** `GET /claims/history`

**查询参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| page | integer | 否 | 1 | 页码 |
| page_size | integer | 否 | 20 | 每页数量 |
| verdict | string | 否 | all | 过滤结论 (SUPPORTED/REFUTED/INCONCLUSIVE) |
| sort_by | string | 否 | created_at | 排序字段 (created_at/confidence) |
| order | string | 否 | desc | 排序方向 (asc/desc) |

**请求示例:**

```bash
curl -X GET "http://localhost:8080/api/claims/history?page=1&page_size=10"
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "claims": [
      {
        "id": "550e8400-e29b-41d4-a716-446655440000",
        "text": "GPT-5 将在 2025 年发布",
        "verdict": "INCONCLUSIVE",
        "verdict_display": "无法判断",
        "confidence": 35,
        "evidence_count": 18,
        "created_at": "2025-03-01T12:00:00Z"
      },
      {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "text": "多模态 AI 将在 2025 年成为主流",
        "verdict": "SUPPORTED",
        "verdict_display": "证明",
        "confidence": 85,
        "evidence_count": 25,
        "created_at": "2025-02-28T09:30:00Z"
      }
    ],
    "pagination": {
      "total": 42,
      "page": 1,
      "page_size": 10,
      "total_pages": 5,
      "has_next": true,
      "has_prev": false
    }
  }
}
```

---

### 3. 获取单个验证结果

获取指定 ID 的详细验证结果。

**端点:** `GET /claims/:id`

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 论点 ID (UUID) |

**请求示例:**

```bash
curl -X GET http://localhost:8080/api/claims/550e8400-e29b-41d4-a716-446655440000
```

**响应:** 与 `POST /verify-claim` 相同

---

### 4. 删除历史记录

删除指定的验证记录。

**端点:** `DELETE /claims/:id`

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 论点 ID (UUID) |

**请求示例:**

```bash
curl -X DELETE http://localhost:8080/api/claims/550e8400-e29b-41d4-a716-446655440000
```

**响应示例:**

```json
{
  "success": true,
  "data": {
    "deleted": true,
    "message": "记录已删除"
  }
}
```

---

### 5. 重新分析

使用最新数据重新分析已有论点。

**端点:** `POST /claims/:id/reanalyze`

**路径参数:**

| 参数 | 类型 | 说明 |
|------|------|------|
| id | string | 论点 ID (UUID) |

**请求示例:**

```bash
curl -X POST http://localhost:8080/api/claims/550e8400-e29b-41d4-a716-446655440000
```

**响应:** 与 `POST /verify-claim` 相同，但会保留原记录并创建新记录

---

### 6. 导出报告

导出验证结果为 PDF 或 Markdown。

**端点:** `GET /claims/:id/export`

**查询参数:**

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| format | string | 否 | pdf | 导出格式 (pdf/markdown/json) |

**请求示例:**

```bash
curl -X GET "http://localhost:8080/api/claims/550e8400-e29b-41d4-a716-446655440000/export?format=markdown" \
  -o report.md
```

**响应:** 文件下载

---

## 数据模型

### Verdict 枚举

```typescript
enum Verdict {
  SUPPORTED = "SUPPORTED",      // 证明
  REFUTED = "REFUTED",          // 证伪
  INCONCLUSIVE = "INCONCLUSIVE"  // 无法判断
}
```

### Confidence Level

```typescript
enum ConfidenceLevel {
  VERY_HIGH = "VERY_HIGH",  // 90-100
  HIGH = "HIGH",            // 70-89
  MEDIUM = "MEDIUM",        // 50-69
  LOW = "LOW",              // 30-49
  VERY_LOW = "VERY_LOW"     // 0-29
}
```

### Source Type

```typescript
enum SourceType {
  OFFICIAL = "official",     // 官方博客/新闻
  MEDIA = "media",           // 媒体报道
  SOCIAL = "social",         // 社交媒体
  ANALYST = "analyst",       // 分析师报告
  COMMUNITY = "community"    // 社区讨论
}
```

---

## 错误处理

### 错误响应格式

```json
{
  "success": false,
  "error": {
    "code": "INVALID_CLAIM",
    "message": "论点文本不能为空",
    "details": {
      "field": "claim",
      "constraint": "min_length=5"
    }
  }
}
```

### 错误码

| 错误码 | HTTP Status | 说明 |
|--------|-------------|------|
| INVALID_CLAIM | 400 | 论点无效（太短、太长、包含非法字符） |
| INVALID_TIME_WINDOW | 400 | 时间窗口超出范围 (1-30天) |
| CLAIM_NOT_FOUND | 404 | 论点 ID 不存在 |
| NO_EVIDENCE_FOUND | 404 | 未找到相关证据 |
| LLM_API_ERROR | 500 | LLM API 调用失败 |
| VECTOR_SEARCH_ERROR | 500 | 向量检索错误 |
| INTERNAL_ERROR | 500 | 内部服务器错误 |
| RATE_LIMIT_EXCEEDED | 429 | 速率限制 |

---

## 速率限制

**MVP:** 无限制（本地使用）

**未来（如部署为公共 API）:**

| 级别 | 限制 |
|------|------|
| 匿名用户 | 10 次/小时 |
| 认证用户 | 100 次/小时 |
| 高级用户 | 1000 次/小时 |

**响应头:**

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1740835200
```

---

## 示例代码

### JavaScript (Fetch API)

```javascript
// 验证论点
async function verifyClaim(claimText) {
  const response = await fetch('http://localhost:8080/api/verify-claim', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      claim: claimText,
      time_window: 7,
      min_confidence: 50
    })
  });

  const result = await response.json();

  if (result.success) {
    console.log('结论:', result.data.verdict_display);
    console.log('置信度:', result.data.confidence);
    console.log('证据数量:', result.data.evidence_summary.total);
    return result.data;
  } else {
    console.error('错误:', result.error.message);
    throw new Error(result.error.message);
  }
}

// 使用示例
verifyClaim('GPT-5 将在 2025 年发布')
  .then(result => {
    // 处理结果
  });
```

### Python (requests)

```python
import requests

def verify_claim(claim_text):
    url = "http://localhost:8080/api/verify-claim"
    payload = {
        "claim": claim_text,
        "time_window": 7,
        "min_confidence": 50
    }

    response = requests.post(url, json=payload)
    result = response.json()

    if result["success"]:
        print(f"结论: {result['data']['verdict_display']}")
        print(f"置信度: {result['data']['confidence']}")
        return result["data"]
    else:
        print(f"错误: {result['error']['message']}")
        raise Exception(result["error"]["message"])

# 使用示例
verify_claim("GPT-5 将在 2025 年发布")
```

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-03-01 | 初始版本 |

---

*本文档是 CLAIM_VERIFICATION_REQUIREMENTS.md 的配套技术规范*

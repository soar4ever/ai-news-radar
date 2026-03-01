# 📋 论点验证功能 - 快速参考

**项目:** AI Signal Board - 论点验证模块
**版本:** v1.0 MVP
**预期交付:** 2025-03-22

---

## 🎯 核心功能

```
用户输入论点 → 系统检索证据 → AI 分析推理 → 返回结论 + 证据链
```

**示例:**
```
输入: "GPT-5 将在 2025 年发布"
      ↓
检索: 最近7天的相关新闻（18条）
      ↓
分析: 支持2条 | 反对1条 | 中性15条
      ↓
结论: 无法判断 - 信息矛盾 (置信度: 35%)
```

---

## 📊 技术栈

| 层级 | 技术 | 说明 |
|------|------|------|
| 前端 | Vanilla JS + CSS3 | 复用现有技术栈 |
| 后端 | Python 3.13 + FastAPI | 轻量级 Web 框架 |
| AI | OpenAI GPT-4o mini | 成本优化 |
| 检索 | 关键词 + 向量 | Phase 2: ChromaDB |
| 存储 | SQLite + JSON | 本地优先 |

---

## 🗂️ 数据库表

```
claims (论点)
  └─ analysis_results (分析结果)
       └─ claim_evidence (关联)
            └─ evidence (证据)

cache (缓存) - 独立表
```

---

## 🔑 API 端点

```
POST   /api/verify-claim      验证论点
GET    /api/claims/history    历史记录
GET    /api/claims/:id        获取详情
DELETE /api/claims/:id        删除记录
POST   /api/claims/:id/reanalyze  重新分析
GET    /api/claims/:id/export     导出报告
```

---

## 📁 文件结构

```
scripts/
  ├── claim_verifier.py       # 主控制器 ⭐
  ├── claim_understander.py   # 论点理解
  ├── evidence_retriever.py   # 证据检索
  ├── claim_analyzer.py       # AI 分析
  └── confidence_scorer.py    # 可信度评分

assets/
  ├── claim-verifier.html     # 新页面
  ├── claim-verifier.js       # 前端逻辑
  └── claim-verifier.css      # 样式

data/
  ├── claims.db               # SQLite
  └── vector_index/           # ChromaDB
```

---

## ⏱️ 开发计划

| 周次 | 任务 | 交付物 |
|------|------|--------|
| Week 1 | 论点理解 + 证据检索 + LLM 集成 | 可验证原型 |
| Week 2 | 结果展示 + API + 错误处理 | MVP 完成 |
| Week 3 | 向量检索 + 可信度评分 + 历史 | 增强功能 |
| Week 4 | 性能优化 + 测试 + 文档 | 正式发布 |

---

## 🎨 UI 组件

```
┌─────────────────────────────────────┐
│ 结论卡片 (VerdictCard)               │
│ 🟢 高度可能 - 置信度 85%             │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 证据卡片 (EvidenceCard)              │
│ 📰 Google Gemini 2.0 发布            │
│ 来源: Google Blog ⭐ 官方            │
│ 相关性: ████████░░ 92%               │
└─────────────────────────────────────┘

┌─────────────────────────────────────┐
│ 置信度条 (ConfidenceBar)             │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│ 0%        50%        75%       100% │
└─────────────────────────────────────┘
```

---

## ✅ 验收标准

### 功能
- [ ] 输入论点后 10 秒内返回结果
- [ ] 至少返回 1 条相关证据（如果有）
- [ ] 置信度分数会根据新证据变化

### 性能
- [ ] 响应时间 < 10 秒
- [ ] 并发支持 10 个请求
- [ ] 缓存命中率 > 30%

### 质量
- [ ] LLM 幻觉率 < 5%
- [ ] 误判率 < 15%

---

## 💰 成本估算

| 项目 | 成本 | 说明 |
|------|------|------|
| OpenAI API | $50/月 | GPT-4o mini |
| 开发时间 | 160h | 4 周 |
| **总计** | **~$50/月** | 不含人力 |

---

## 🔧 技术依赖

### 新增 Python 包

```txt
openai>=1.0.0              # LLM API
sentence-transformers      # 向量化
chromadb                   # 向量数据库
spaCy>=3.0.0              # NLP
fastapi>=0.100.0          # Web 框架
uvicorn>=0.23.0           # ASGI 服务器
```

### 新增 npm 包（可选）

```json
{
  "chart.js": "^4.0.0",     // 可视化
  "markdown-it": "^14.0.0"  // Markdown 渲染
}
```

---

## 🚀 快速启动

```bash
# 1. 安装依赖
cd /Users/nick/Claude\ Code/ai-news-radar
pip install -r requirements.txt
pip install openai sentence-transformers chromadb spacy fastapi uvicorn

# 2. 初始化数据库
python scripts/init_db.py

# 3. 启动服务（开发）
uvicorn scripts.api:app --reload --port 8080

# 4. 访问界面
open http://localhost:8080/claim-verifier.html
```

---

## 📚 完整文档

| 文档 | 大小 | 描述 |
|------|------|------|
| [需求文档](./CLAIM_VERIFICATION_REQUIREMENTS.md) | 25KB | 完整需求规格 ⭐ |
| [API 规范](./API_SPECIFICATION.md) | 10KB | 接口技术规范 |
| [数据库设计](./DATABASE_SCHEMA.md) | 12KB | Schema 和 ER 图 |
| [UI/UX 设计](./UI_UX_DESIGN.md) | 23KB | 界面和交互 |
| [文档索引](./README.md) | 5.7KB | 阅读指南 |

---

## 🎯 下一步

**请 Nick:**

1. 📖 阅读 [需求文档](./CLAIM_VERIFICATION_REQUIREMENTS.md)
2. ✏️ 在 [文档索引](./README.md) 中标注修改意见
3. 💬 提出疑问或补充需求
4. ✅ 确认后开始编码

**预计启动:** 2025-03-02
**预计交付:** 2025-03-22

---

*快速参考卡片 v1.0*

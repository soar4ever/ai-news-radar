# 论点验证功能 - 文档索引

**项目:** AI Signal Board - 论点验证模块
**版本:** v1.0
**更新:** 2025-03-01

---

## 📚 文档导航

### 核心文档

1. **[需求文档](./CLAIM_VERIFICATION_REQUIREMENTS.md)** ⭐ 主文档

   - 项目概述

   - 用户故事

   - 功能需求（MVP + 增强）

   - 技术规格

   - 验收标准

   - 实施计划

2. **[API 技术规范](./API_SPECIFICATION.md)**

   - REST API 端点定义

   - 请求/响应格式

   - 错误处理

   - 速率限制

   - 示例代码

3. **[数据库 Schema](./DATABASE_SCHEMA.md)**

   - 表结构设计

   - 索引策略

   - ER 图

   - 查询示例

   - 维护指南

4. **[UI/UX 设计规范](./UI_UX_DESIGN.md)**

   - 页面布局

   - 组件设计

   - 交互流程

   - 视觉规范

   - 响应式设计

---

## 📋 快速开始

### 文档阅读顺序

**第一次阅读（了解功能）：**

1. 需求文档 → 了解整体需求

2. UI/UX 设计 → 看界面原型

3. 验收标准 → 了解如何判断完成

**开发前准备：**

1. 需求文档 → 功能需求章节

2. API 技术规范 → 接口设计

3. 数据库 Schema → 数据模型

4. UI/UX 设计 → 前端实现

**开发中参考：**

- API 技术规范 → 接口调用

- 数据库 Schema → SQL 查询

- UI/UX 设计 → 组件样式

---

## 🎯 关键决策点

### 需要你确认的问题

#### 1. 功能范围 (Priority)

**MVP (必做):**

- [x] 论点输入界面

- [x] 关键词检索

- [x] LLM 分析（GPT-4o mini）

- [x] 基础结果展示

**Phase 2 (增强):**

- [ ] 向量语义检索

- [ ] 可信度评分算法

- [ ] 历史记录

- [ ] 缓存机制

**问题:** MVP 是否满足你的预期？是否需要调整功能优先级？

<!-- COMMENT: 没问题 -->

---

#### 2. 时间窗口 (Time Window)

**当前设计:** 1天、3天、7天、30天

**已确认调整:**

- ✅ 添加"自定义"选项（用户输入具体日期范围）
- ✅ 添加日期选择器组件

<!-- COMMENT: 需要自定义选项。-->

---

#### 3. 置信度阈值 (Min Confidence)

**当前设计:** 全部、>50%、>70%

**问题:**

- 是否需要更细粒度的控制（如 10% 步进）？

- 是否需要"只显示高置信度结果"选项？

<!-- COMMENT: 1）不用更细粒度的控制；2）不需要。-->

---

#### 4. LLM 模型选择 (Model)

**当前设计:**

- MVP: GPT-4o mini（成本优化）

- 未来: Claude 3.5 Sonnet（质量优化）

**已确认调整:**

- ✅ 集成 cc switch，让用户自主选择模型
- ✅ 支持: fast (GPT-4o mini) / standard (GPT-4o) / smart (Claude 3.5 Sonnet)
- ✅ 复用 `~/.claude/skills/PAI/Tools/Inference.ts`

<!-- COMMENT: 让用户选择模型。是不是可以对接cc switch实现用户自主选择模型？-->

---

#### 5. 缓存策略 (Cache)

**当前设计:**

- 缓存键：论点文本的哈希值

- TTL：24小时

- 命中提示："这是缓存结果"

**简单说明:**

缓存就是"记住之前的答案"。例如：你问"GPT-5何时发布"，系统分析后记住结果，24小时内再问同样问题时直接返回旧结果（省钱省时间）。

**已确认调整:**

- ✅ 添加"强制重新分析"按钮
- ✅ 简化缓存提示文案

<!-- COMMENT: 这部分没太理解，我不太懂技术 -->

---

#### 6. 历史记录 (History) + 博客发布

**当前设计:**

- 自动保存所有验证结果

- 可以查看、删除、重新分析

- 本地 SQLite 存储

**已确认调整:**

- ✅ 添加"收藏"功能（标记重要结果）
- ✅ 集成 GitHub 博客发布功能
  - 博客仓库: https://github.com/soar4ever/blog-test
  - 发布方式: 生成 Markdown → GitHub API 创建文件到 `docs/` 目录
  - GitHub Actions 自动构建部署
- ❌ 移除"导出所有历史"功能

<!-- COMMENT:

1. 需要收藏功能；

2. 不需要导出所有历史功能；

3. 需要云端同步，支持把分析结论发布到我的GitHub博客上。

-->

---

#### 7. UI/UX 偏好 (Design)

**当前设计:**

- 结论卡片：大图标 + 颜色区分

- 证据时间线：垂直时间轴

- 加载动画：步骤进度条

**问题:**

- 是否喜欢这个设计风格？

- 是否需要更简洁的版本？

- 颜色方案是否满意？

<!-- COMMENT: 一期简单点就好，这些没问题。-->

---

## 📝 审查清单

### 需求确认

请在审查文档后，确认以下问题：

- [x] 功能需求是否完整？

- [x] UI/UX 设计是否满意？

- [x] 技术方案是否可行？

- [x] 时间线是否合理？

 <!-- COMMENT:  - [ ] 时间可以更紧凑些，你写代码的能力太强了！-->

- [x] 是否有遗漏或需要补充的部分？



### 优先级调整

请标注每个功能模块的优先级：

| 功能     | 优先级 | 备注 |
| ------ | --- | -- |
| 论点输入界面 | P0  | -  |
| 关键词检索  | P0  | -  |
| LLM 分析 | P0  | -  |
| 结果展示   | P0  | -  |
| 向量检索   | P1  | -  |
| 可信度评分  | P1  | -  |
| 历史记录   | P1  | -  |
| 缓存机制   | P1  | -  |
| 导出报告   | P2  | -  |
| 订阅提醒   | P3  | -  |

---

## 🚀 下一步行动

### 确认后开始开发

1. **确认需求:** 在本文档中标注你的修改意见

2. **讨论疑问:** 提出任何不清楚的地方

3. **批准开始:** 确认后我们立即开始编码

### 开发流程

```
Week 1: MVP 核心功能
├─ 论点理解 + 证据检索
├─ LLM 分析集成
└─ 基础 UI + API

Week 2: 完善功能
├─ 结果展示优化
├─ 错误处理
└─ 测试

Week 3: 增强功能
├─ 向量检索（可选）
├─ 可信度评分（可选）
└─ 历史记录（可选）

Week 4: 优化上线
├─ 性能优化
├─ UI/UX 改进
└─ 部署
```

---

## 💬 反馈方式

请直接在文档中：

1. **修改内容:** 直接编辑文档，标注修改原因

2. **添加评论:** 使用 `<!-- COMMENT: 你的评论 -->` 添加注释

3. **提出疑问:** 在文档末尾添加"疑问"章节

4. **确认无异议:** 回复"✅ 确认，可以开始开发"

---

## 📊 项目估算

### 时间估算

| 阶段     | 工作量        | 说明      |
| ------ | ---------- | ------- |
| 需求确认   | 1天         | 等待你的反馈  |
| MVP 开发 | 10天        | 核心功能    |
| 增强功能   | 5天         | 可选      |
| 测试优化   | 3天         | 质量保证    |
| **总计** | **15-19天** | 约 3-4 周 |

### 成本估算

| 项目         | 成本       | 说明          |
| ---------- | -------- | ----------- |
| OpenAI API | \~\$50/月 | GPT-4o mini |
| 开发时间       | 160h     | 4周 × 40h    |
| **总成本**    | \~\$50/月 | 不含人力        |

---

## 🎉 预期成果

完成后你将拥有：

✅ 一个基于真实 AI 新闻的论点验证系统
✅ 智能的证据检索和 AI 分析
✅ 清晰的可视化结果展示
✅ 完整的 API 和文档
✅ 可扩展的架构（支持未来增强）

---

## 📧 联系方式

有任何问题随时问我：

- 在此文档中添加评论

- 直接提出疑问

- 要求修改或补充

---

**期待你的反馈！** 🚀

---

## 🎯 博客发布功能 - 技术方案

### 博客仓库信息

- **仓库:** https://github.com/soar4ever/blog-test
- **类型:** Node.js 项目 + GitHub Actions
- **文章目录:** `docs/`
- **文章格式:** Markdown

### 实现方案

#### 方案 A: GitHub API（推荐）

**流程:**

```
1. 用户点击"发布到博客"按钮
   ↓
2. 生成标准 Markdown 格式
   ↓
3. 调用 GitHub API 创建文件
   - PUT /repos/soar4ever/blog-test/contents/docs/claim-{timestamp}.md
   - 提交信息: "Add claim analysis: {论点标题}"
   ↓
4. GitHub Actions 自动触发构建
   ↓
5. 博客自动部署
```

**代码示例:**

```python
import requests
import base64
from datetime import datetime

def publish_to_blog(claim_id, claim_text, analysis_result):
    """发布分析结果到 GitHub 博客"""

    # 1. 生成 Markdown
    markdown = generate_blog_markdown(claim_text, analysis_result)

    # 2. 构造 GitHub API 请求
    url = "https://api.github.com/repos/soar4ever/blog-test/contents/docs/"
    filename = f"claim-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"

    payload = {
        "message": f"Add claim analysis: {claim_text[:30]}...",
        "content": base64.b64encode(markdown.encode()).decode()
    }

    # 3. 使用 GitHub Token（需配置）
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    response = requests.put(url + filename, json=payload, headers=headers)
    return response.status_code == 201
```

**Markdown 模板:**

```markdown
---
title: "论点验证: {claim_text}"
date: {date}
tags: [AI, 论点验证, 分析]
---

## 🎯 论点

{claim_text}

## ✅ 结论

**{verdict}** - 置信度: {confidence}%

{reasoning}

## 📊 证据分布

- 支持: {supporting_count}
- 反对: {refuting_count}
- 中性: {neutral_count}

## 📚 证据链

### 支持证据

{supporting_evidence_list}

### 反对证据

{refuting_evidence_list}

## 🔗 原始数据

分析时间: {created_at}
证据来源: AI Signal Board - 论点验证模块
---
```

#### 方案 B: Git Commit（备选）

**流程:**

```
1. 将 blog-test 添加为 submodule
2. 生成 Markdown 文件
3. git commit + git push
4. GitHub Actions 自动部署
```

### 配置要求

**需要配置:**

1. **GitHub Token** - 创建 Personal Access Token
   - 权限: `repo` (完整仓库访问)
   - 存储位置: 环境变量或配置文件

2. **配置文件:** `config/blog_config.json`

```json
{
  "blog_repo": "soar4ever/blog-test",
  "github_token_env": "GITHUB_TOKEN",
  "default_branch": "main",
  "content_dir": "docs"
}
```

### UI 设计

**发布按钮:**

```
┌─────────────────────────────────────────┐
│ [📌 收藏]  [📤 发布到博客]  [🔄 重新分析] │
└─────────────────────────────────────────┘
```

**发布对话框:**

```
┌─────────────────────────────────────────┐
│ 发布到博客                               │
├─────────────────────────────────────────┤
│                                         │
│ 博客: soar4ever/blog-test                │
│ 目录: docs/                              │
│ 文件名: claim-20250301-120000.md         │
│                                         │
│ [✓] 自动添加标签                         │
│ [✓] 包含完整证据链                       │
│                                         │
│ [取消]  [确认发布]                       │
└─────────────────────────────────────────┘
```

### 验收标准

- [ ] 生成的 Markdown 格式正确
- [ ] 成功通过 GitHub API 创建文件
- [ ] GitHub Actions 自动触发部署
- [ ] 文件出现在博客仓库的 `docs/` 目录
- [ ] 博客网站正确显示新文章

---

*本文档由 PAI 算法驱动的 AI Assistant 生成*
*版本: v1.1 | 最后更新: 2025-03-01*
*更新内容: 添加博客发布技术方案*

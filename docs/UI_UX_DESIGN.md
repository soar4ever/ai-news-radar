# UI/UX 设计规范

**系统:** AI Signal Board - 论点验证模块
**版本:** v1.0
**更新:** 2025-03-01

---

## 目录
1. [设计原则](#设计原则)
2. [页面布局](#页面布局)
3. [组件设计](#组件设计)
4. [交互流程](#交互流程)
5. [视觉规范](#视觉规范)
6. [响应式设计](#响应式设计)
7. [无障碍访问](#无障碍访问)

---

## 设计原则

### 核心原则

1. **清晰优先** - 信息层次清晰，一目了然
2. **快速反馈** - 实时状态更新，减少等待焦虑
3. **渐进披露** - 复杂信息分步展示
4. **可操作性** - 每个结果都可追踪和验证

### 设计语言

- 简洁、专业、可信
- 与现有 AI Signal Board 风格一致
- 数据可视化友好

---

## 页面布局

### 整体结构

```
┌─────────────────────────────────────────────────────────┐
│  Header (导航栏)                                         │
│  AI Signal Board    [新闻雷达] [论点验证]               │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Hero Section (标题区)                                   │
│  🎯 论点验证 - 基于 AI 新闻的智能分析                   │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Input Section (输入区)                                  │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 请输入你想验证的论点或声明...                     │  │
│  └──────────────────────────────────────────────────┘  │
│  时间范围: [7天 ▼]  置信度: [全部 ▼]  [🔍 开始验证]    │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Loading State (加载状态) - 验证中显示                   │
│  ⏳ 正在分析... (2/4: 检索证据)                         │
└─────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────┐
│  Result Section (结果区) - 验证完成后显示                │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 🟢 高度可能 - 置信度 85%                          │  │
│  └──────────────────────────────────────────────────┘  │
│  📊 证据分布: 支持 15 | 反对 0 | 中性 3                 │
│  📚 证据链                                             │
│  ┌──────────────────────────────────────────────────┐  │
│  │ 证据卡片 1                                        │  │
│  │ 证据卡片 2                                        │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## 组件设计

### 1. 输入组件 (InputSection)

**状态:** 默认 / 聚焦 / 错误

```
默认状态:
┌────────────────────────────────────────────────────┐
│ 请输入你想验证的论点或声明...                        │
└────────────────────────────────────────────────────┘

聚焦状态:
┌────────────────────────────────────────────────────┐
│ GPT-5 将在 2025 年发布 |                            │
└────────────────────────────────────────────────────┘
   ───────────────── ↑ 光标

错误状态:
┌────────────────────────────────────────────────────┐
│ GPT                                                │
└────────────────────────────────────────────────────┘
⚠️ 论点太短，请至少输入 5 个字符
```

**参数选择器:**

```
时间范围:
┌────────────────┐
│ 1天  │         │
│ 3天  │         │
│ 7天  │ ✓ 当前  │
│ 30天 │         │
│ 自定义 │       │
└────────────────┘

置信度阈值:
┌────────────────────────────────────┐
│ ○ 全部    ○ >50%    ● >70%       │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━   │
│ 0%         50%        70%      100% │
└────────────────────────────────────┘
```

### 2. 结论卡片 (VerdictCard)

**三种状态:**

**证明 (SUPPORTED):**
```
┌────────────────────────────────────────────────────┐
│  ┌──┐                                             │
│  │✓ │  高度可能                                   │
│  └──┘  置信度: 85%                                │
│                                                     │
│  基于最近7天的18条新闻分析，多模态AI在2025年      │
│  成为 mainstream 的趋势得到了多方支持。          │
│                                                     │
│  [查看详细推理]  [查看证据链]                       │
└────────────────────────────────────────────────────┘
```

**证伪 (REFUTED):**
```
┌────────────────────────────────────────────────────┐
│  ┌──┐                                             │
│  │✗ │  证伪                                       │
│  └──┘  置信度: 75%                                │
│                                                     │
│  基于5条明确的反对证据，该论点被证明为错误。      │
│                                                     │
│  [查看详细推理]  [查看证据链]                       │
└────────────────────────────────────────────────────┘
```

**无法判断 (INCONCLUSIVE):**
```
┌────────────────────────────────────────────────────┐
│  ┌──┐                                             │
│  │? │  无法判断                                   │
│  └──┘  置信度: 35%                                │
│                                                     │
│  信息存在矛盾，既有支持证据也有反对证据。        │
│  需要更多信息才能得出结论。                        │
│                                                     │
│  [查看详细推理]  [查看证据链]                       │
└────────────────────────────────────────────────────┘
```

### 3. 置信度指示器 (ConfidenceIndicator)

```
数值显示:
┌────────────────────────────────────────────────┐
│ 置信度: 85%                                    │
│ ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  │
│ 0%        25%        50%        75%       100% │
│                        ▲                       │
│                   当前值                       │
└────────────────────────────────────────────────┘

等级标签:
- 90-100%: 非常确定 🟢
- 70-89%: 高度可能 🟢
- 50-69%: 中等可能 🟡
- 30-49%: 低可能 🟠
- 0-29%: 非常不确定 🔴
```

### 4. 证据卡片 (EvidenceCard)

```
┌────────────────────────────────────────────────────┐
│ 📰 Google Gemini 2.0 发布                         │
│                                                     │
│ 来源: Google Blog ⭐ 官方                          │
│ 时间: 02-28 10:00                                  │
│ 相关性: ████████░░ 92%                            │
│                                                     │
│ 摘要: Google 今天发布了多模态能力更强的 Gemini... │
│                                                     │
│ [🔗 查看原文]  [📌 标记为关键证据]                │
└────────────────────────────────────────────────────┘

证据类型标签:
- [支持] 🟢 绿色
- [反对] 🔴 红色
- [中性] ⚪ 灰色

来源图标:
- ⭐ 官方 (official)
- 📰 媒体 (media)
- 🐦 社交 (social)
- 📊 分析师 (analyst)
- 💬 社区 (community)
```

### 5. 证据时间线 (EvidenceTimeline)

```
证据时间线（最近7天）

02-28  │  ●───────────────────────────────────────
       │  Google Gemini 2.0 (支持)
       │
02-27  │  ●────────────────────────
       │  OpenAI GPT-4V 升级 (支持)
       │
02-26  │  ●───────────────────────────────────────
       │  Anthropic Claude 多模态 (支持)
       │
02-25  │
       │
02-24  │  ●────────────────
       │  行业分析师预测 (中性)
       │
       └───────────────────────────────────────
         1天    2天    3天    4天    5天    6天    7天
```

### 6. 加载动画 (LoadingAnimation)

```
步骤显示:

⏳ 正在分析论点... (1/4)
  ✓ 提取关键词和实体
  → 检索相关证据
  ⏳ AI 智能分析
  ⏳ 生成结论

进度条:
┌────────────────────────────────────────────────┐
│ ████████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ 40% - 正在检索证据...                          │
└────────────────────────────────────────────────┘

骨架屏:
┌────────────────────────────────────────────────┐
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
│ ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ │
└────────────────────────────────────────────────┘
```

---

## 交互流程

### 主流程

```
1. 用户输入论点
   ├─ 输入框实时验证（长度、格式）
   ├─ 显示字符计数
   └─ 自动保存草稿（LocalStorage）

2. 点击"开始验证"
   ├─ 显示加载动画
   ├─ 禁用输入和按钮
   └─ 显示进度步骤

3. 分析完成
   ├─ 滚动到结果区域
   ├─ 淡入动画显示结果
   ├─ 保存到历史记录
   └─ 启用重新分析按钮

4. 查看证据
   ├─ 点击证据卡片展开详情
   ├─ 点击"查看原文"打开新标签页
   └─ 可标记关键证据

5. 调整参数重新验证
   ├─ 修改时间范围或置信度
   ├─ 点击"重新分析"
   └─ 对比新旧结果
```

### 边界情况

**空结果:**
```
┌────────────────────────────────────────────────┐
│  😔 未找到相关证据                             │
│                                                 │
│  在过去7天的新闻中，没有找到与该论点相关的      │
│  证据。建议：                                  │
│  • 扩大时间范围                                │
│  • 调整论点表述                                │
│  • 确认是否为 AI/科技领域                      │
│                                                 │
│  [修改参数]  [重新输入]                        │
└────────────────────────────────────────────────┘
```

**错误状态:**
```
┌────────────────────────────────────────────────┐
│  ⚠️ 分析失败                                   │
│                                                 │
│  LLM API 调用超时。请稍后重试。                │
│                                                 │
│  [重试]  [返回]                                │
└────────────────────────────────────────────────┘
```

---

## 视觉规范

### 颜色系统

**主色调:**
```css
--color-primary: #3B82F6;        /* 蓝色 - 主品牌色 */
--color-primary-hover: #2563EB;
--color-primary-light: #DBEAFE;
```

**结论色:**
```css
--color-supported: #10B981;      /* 绿色 - 证明 */
--color-refuted: #EF4444;        /* 红色 - 证伪 */
--color-inconclusive: #6B7280;   /* 灰色 - 无法判断 */
```

**置信度色:**
```css
--color-very-high: #059669;      /* 90-100% 深绿 */
--color-high: #10B981;           /* 70-89% 绿色 */
--color-medium: #F59E0B;         /* 50-69% 橙色 */
--color-low: #F97316;            /* 30-49% 深橙 */
--color-very-low: #DC2626;       /* 0-29% 红色 */
```

**中性色:**
```css
--color-text-primary: #111827;   /* 主要文本 */
--color-text-secondary: #6B7280; /* 次要文本 */
--color-text-tertiary: #9CA3AF;  /* 辅助文本 */
--color-border: #E5E7EB;         /* 边框 */
--color-bg: #F9FAFB;             /* 背景 */
--color-surface: #FFFFFF;        /* 卡片背景 */
```

### 字体系统

```css
--font-family-base: "Noto Sans SC", sans-serif;
--font-family-heading: "Bricolage Grotesque", sans-serif;

--font-size-xs: 0.75rem;    /* 12px */
--font-size-sm: 0.875rem;   /* 14px */
--font-size-base: 1rem;     /* 16px */
--font-size-lg: 1.125rem;   /* 18px */
--font-size-xl: 1.5rem;     /* 24px */
--font-size-2xl: 2rem;      /* 32px */
--font-size-3xl: 2.5rem;    /* 40px */
```

### 间距系统

```css
--spacing-1: 0.25rem;  /* 4px */
--spacing-2: 0.5rem;   /* 8px */
--spacing-3: 0.75rem;  /* 12px */
--spacing-4: 1rem;     /* 16px */
--spacing-5: 1.25rem;  /* 20px */
--spacing-6: 1.5rem;   /* 24px */
--spacing-8: 2rem;     /* 32px */
--spacing-10: 2.5rem;  /* 40px */
--spacing-12: 3rem;    /* 48px */
```

### 圆角

```css
--radius-sm: 0.25rem;   /* 4px */
--radius-base: 0.5rem;  /* 8px */
--radius-lg: 0.75rem;   /* 12px */
--radius-xl: 1rem;      /* 16px */
--radius-full: 9999px;  /* 圆形 */
```

### 阴影

```css
--shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
--shadow-base: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
--shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
--shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
```

---

## 响应式设计

### 断点

```css
--breakpoint-sm: 640px;   /* 手机 */
--breakpoint-md: 768px;   /* 平板 */
--breakpoint-lg: 1024px;  /* 桌面 */
--breakpoint-xl: 1280px;  /* 大屏 */
```

### 布局适配

**桌面 (>1024px):**
- 双栏布局（输入 + 结果并排）
- 宽度最大 1200px
- 侧边栏显示历史记录

**平板 (768px-1024px):**
- 单栏布局
- 输入和结果上下排列
- 历史记录可折叠

**手机 (<768px):**
- 单栏布局
- 简化参数选择
- 底部导航

---

## 动画规范

### 过渡时长

```css
--duration-fast: 150ms;     /* 快速反馈 */
--duration-base: 200ms;     /* 标准过渡 */
--duration-slow: 300ms;     /* 复杂动画 */
--duration-slower: 500ms;   /* 页面切换 */
```

### 缓动函数

```css
--ease-in: cubic-bezier(0.4, 0, 1, 1);
--ease-out: cubic-bezier(0, 0, 0.2, 1);
--ease-in-out: cubic-bezier(0.4, 0, 0.2, 1);
```

### 常用动画

**淡入:**
```css
@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
```

**上滑淡入:**
```css
@keyframes slideUpFade {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

**旋转（加载）:**
```css
@keyframes spin {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}
```

---

## 无障碍访问

### ARIA 标签

```html
<!-- 输入框 -->
<label for="claim-input">论点输入</label>
<input
  id="claim-input"
  type="text"
  aria-label="请输入你想验证的论点"
  aria-describedby="claim-help"
/>
<div id="claim-help">例如: GPT-5 将在 2025 年发布</div>

<!-- 结论卡片 -->
<div
  role="region"
  aria-live="polite"
  aria-label="验证结果"
>
  <h2>高度可能 - 置信度 85%</h2>
</div>
```

### 键盘导航

- `Tab`: 焦点切换
- `Enter`: 提交表单
- `Escape`: 取消/关闭
- `Space`: 切换开关/复选框

### 焦点指示

```css
:focus-visible {
  outline: 2px solid var(--color-primary);
  outline-offset: 2px;
}
```

---

## 组件代码示例

### HTML 结构

```html
<section class="claim-verifier">
  <!-- 输入区 -->
  <div class="input-section">
    <h1>🎯 论点验证</h1>
    <p class="subtitle">基于 AI 新闻的智能分析</p>

    <div class="input-group">
      <textarea
        id="claim-input"
        placeholder="请输入你想验证的论点或声明..."
        rows="3"
      ></textarea>
      <span class="char-count">0/500</span>
    </div>

    <div class="parameters">
      <div class="param-group">
        <label>时间范围</label>
        <select id="time-window">
          <option value="1">1天</option>
          <option value="3">3天</option>
          <option value="7" selected>7天</option>
          <option value="30">30天</option>
        </select>
      </div>

      <div class="param-group">
        <label>置信度阈值</label>
        <select id="min-confidence">
          <option value="0" selected>全部</option>
          <option value="50">> 50%</option>
          <option value="70">> 70%</option>
        </select>
      </div>

      <button id="verify-btn" class="btn-primary">
        🔍 开始验证
      </button>
    </div>
  </div>

  <!-- 加载状态 -->
  <div id="loading-state" class="loading-state hidden">
    <div class="spinner"></div>
    <p>正在分析... (1/4: 检索证据)</p>
  </div>

  <!-- 结果区 -->
  <div id="result-section" class="result-section hidden">
    <div class="verdict-card verdict-supported">
      <div class="verdict-icon">✓</div>
      <div class="verdict-content">
        <h2>高度可能</h2>
        <p class="confidence">置信度: 85%</p>
        <p class="reasoning">基于最近7天的18条新闻分析...</p>
      </div>
    </div>

    <div class="evidence-summary">
      <span>支持: 15</span>
      <span>反对: 0</span>
      <span>中性: 3</span>
    </div>

    <h3>证据链</h3>
    <div class="evidence-list">
      <!-- 证据卡片由 JS 生成 -->
    </div>
  </div>
</section>
```

### CSS 样式

```css
/* 结论卡片 */
.verdict-card {
  display: flex;
  gap: var(--spacing-4);
  padding: var(--spacing-6);
  border-radius: var(--radius-lg);
  background: var(--color-surface);
  box-shadow: var(--shadow-md);
  animation: slideUpFade var(--duration-slow) var(--ease-out);
}

.verdict-supported {
  border-left: 4px solid var(--color-supported);
}

.verdict-refuted {
  border-left: 4px solid var(--color-refuted);
}

.verdict-inconclusive {
  border-left: 4px solid var(--color-inconclusive);
}

/* 置信度条 */
.confidence-bar {
  height: 8px;
  background: var(--color-border);
  border-radius: var(--radius-full);
  overflow: hidden;
}

.confidence-fill {
  height: 100%;
  background: linear-gradient(90deg,
    var(--color-very-low) 0%,
    var(--color-low) 25%,
    var(--color-medium) 50%,
    var(--color-high) 75%,
    var(--color-very-high) 100%
  );
  transition: width var(--duration-base) var(--ease-out);
}

/* 证据卡片 */
.evidence-card {
  padding: var(--spacing-4);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-base);
  background: var(--color-surface);
  transition: all var(--duration-base) var(--ease-out);
  cursor: pointer;
}

.evidence-card:hover {
  box-shadow: var(--shadow-md);
  transform: translateY(-2px);
}

.evidence-card.type-supporting {
  border-left: 3px solid var(--color-supported);
}

.evidence-card.type-refuting {
  border-left: 3px solid var(--color-refuted);
}

.evidence-card.type-neutral {
  border-left: 3px solid var(--color-inconclusive);
}
```

---

## 更新日志

| 版本 | 日期 | 变更 |
|------|------|------|
| v1.0 | 2025-03-01 | 初始版本 |

---

*本文档是 CLAIM_VERIFICATION_REQUIREMENTS.md 的配套设计规范*

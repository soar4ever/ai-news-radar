# API Keys 配置说明

## Anthropic API (Claude)

论点验证系统使用 Anthropic Claude API 进行智能分析。

### 获取 API Key

1. 访问 https://console.anthropic.com/
2. 注册/登录账号
3. 进入 API Keys 页面
4. 创建新的 API Key

### 配置方法

**方法 1: 环境变量（推荐）**

```bash
export ANTHROPIC_API_KEY=sk-ant-xxxxx
```

**方法 2: .env 文件**

创建 `.env` 文件（记得添加到 .gitignore）：

```bash
ANTHROPIC_API_KEY=sk-ant-xxxxx
```

然后使用：

```bash
source .env  # 或使用 dotenv 库
```

### 模型选择

系统支持以下模型：

- **fast**: `claude-3-5-haiku-20241022` - 快速便宜，适合简单分析
- **standard**: `claude-sonnet-4-20250514` - 标准质量，平衡性能
- **smart**: `claude-sonnet-4-20250514` - 最强模型

### 成本估算

基于 Claude Sonnet 4.5:
- 每次分析约消耗 500-1000 tokens
- 成本约 $0.002-0.005 每次
- 100 次分析约 $0.20-0.50

### 降级机制

如果 API Key 未配置或 API 调用失败，系统会自动降级到规则引擎，确保功能可用。

---

## 配置优先级

1. 环境变量 `ANTHROPIC_API_KEY`
2. .env 文件
3. 降级到规则引擎

---

## 安全提醒

⚠️ **重要:**

- 永远不要将 API Key 提交到 Git 仓库
- 使用 `.gitignore` 排除 `.env` 文件
- 在生产环境使用环境变量
- 定期轮换 API Key

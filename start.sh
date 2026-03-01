#!/bin/bash
# 快速启动脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║        论点验证系统 - 快速启动                          ║"
echo "╠════════════════════════════════════════════════════════════╣"
echo "║                                                           ║"
echo "║  检查环境...                                             ║"

# 检查 Python 环境
if [ ! -d ".venv" ]; then
    echo "❌ 虚拟环境不存在，请先创建:"
    echo "   python3 -m venv .venv"
    exit 1
fi

echo "✅ 虚拟环境存在"

# 检查依赖
echo "📦 检查依赖..."
.venv/bin/pip list | grep -E "(anthropic|fastapi)" > /dev/null
if [ $? -ne 0 ]; then
    echo "⚠️  依赖未完全安装，正在安装..."
    .venv/bin/pip install -q anthropic fastapi uvicorn
fi

echo "✅ 依赖已安装"

# 检查 API Key
if [ -z "$ANTHROPIC_API_KEY" ]; then
    if [ -f ".env" ]; then
        echo "📝 从 .env 文件加载配置..."
        set -a
        source .env
    else
        echo ""
        echo "⚠️  未配置 Anthropic API Key"
        echo ""
        echo "请选择配置方式:"
        echo "  1. 设置环境变量:"
        echo "     export ANTHROPIC_API_KEY=your_key_here"
        echo ""
        echo "  2. 创建 .env 文件:"
        echo "     cp .env.example .env"
        echo "     # 编辑 .env 文件，填入你的 API Key"
        echo ""
        echo "  3. 继续使用规则引擎（无需 API Key）"
        echo ""
        read -p "选择 (1/2/3): " choice

        case $choice in
            1)
                read -p "请输入你的 API Key: " api_key
                export ANTHROPIC_API_KEY=$api_key
                echo "✅ API Key 已设置（当前会话有效）"
                ;;
            2)
                cp .env.example .env
                echo "✅ 已创建 .env 文件"
                echo "📝 请编辑 .env 文件并填入你的 API Key"
                echo "   然后重新运行此脚本"
                exit 0
                ;;
            3)
                echo "✅ 继续使用规则引擎"
                ;;
            *)
                echo "❌ 无效选择"
                exit 1
                ;;
        esac
    fi
fi

if [ -n "$ANTHROPIC_API_KEY" ]; then
    echo "✅ API Key 已配置"
fi

echo ""
echo "╚════════════════════════════════════════════════════════════╝"
echo ""
echo "🚀 启动服务器..."
echo ""
echo "   API 文档: http://localhost:8080/docs"
echo "   Web UI:   http://localhost:8080/claim-verifier.html"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

# 启动服务器
.venv/bin/python scripts/api_server.py

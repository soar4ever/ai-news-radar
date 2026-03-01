# Git 工作流参考

## 远程仓库配置

- **origin**: https://github.com/soar4ever/ai-news-radar.git (你的 fork)
- **upstream**: https://github.com/LearnPrompt/ai-news-radar.git (原仓库)

## 常用命令

### 开发新功能
```bash
# 从 master 创建新的 feature 分支
git checkout master
git pull upstream master
git checkout -b feature/your-feature-name

# 开发完成后推送到你的 fork
git push origin feature/your-feature-name
```

### 同步上游更新
```bash
# 更新上游的 master 到本地
git checkout master
git pull upstream master

# 推送到你的 fork
git push origin master
```

### 贡献 PR 到原仓库
```bash
# 1. 推送 feature 分支到你的 fork
git push origin feature/your-feature-name

# 2. 在 GitHub 上创建 PR:
#    从: soar4ever/ai-news-radar/feature/your-feature-name
#    到: LearnPrompt/ai-news-radar/master
```

### 查看分支
```bash
git branch -a  # 查看所有分支
git status     # 查看当前状态
```

## 当前分支
- feature/initial-setup (开发分支)
- master (主分支，跟踪 upstream)

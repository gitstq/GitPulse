# GitPulse

🚀 **AI驱动的Git工作流智能助手** | AI-Powered Git Workflow Intelligence Assistant

GitPulse是一个轻量级、零依赖的Python CLI工具，为开发者提供智能Git工作流辅助。它集成了AI能力，帮助生成符合规范的提交信息、推荐分支名称、提供工作流建议，并自动生成PR描述。

## ✨ 核心特性

- 🤖 **AI智能提交** - 基于代码变更自动生成Conventional Commits格式的提交信息
- 🌿 **分支建议** - 智能推荐符合规范的分支名称
- 🔄 **工作流指导** - 根据当前状态推荐最佳Git操作流程
- 📝 **PR自动化** - 自动生成Pull Request描述
- ✅ **规范验证** - 验证提交信息是否符合团队规范
- 🔌 **多AI后端** - 支持OpenAI、Anthropic、OpenRouter、Ollama等多种AI提供商
- 🎯 **零依赖** - 纯Python标准库实现，无需额外依赖

## 🚀 快速开始

### 安装

```bash
# 使用pip安装
pip install gitpulse

# 或使用gitpulse缩写
gp --help
```

### 初始化配置

```bash
# 运行初始化向导
gitpulse setup
```

### 基本使用

```bash
# 查看Git状态
gitpulse status

# 获取提交建议
gitpulse suggest

# 获取分支建议
gitpulse branch

# 获取工作流建议
gitpulse workflow

# 生成PR描述
gitpulse pr

# 验证提交信息
gitpulse validate "feat(auth): add user login"
```

## 📖 详细文档

详见 [GitHub Wiki](https://github.com/gitstq/GitPulse/wiki)

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

MIT License

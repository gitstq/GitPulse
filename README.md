<div align="center">

# 🚀 GitPulse

**AI驱动的Git工作流智能助手** | AI-Powered Git Workflow Intelligence Assistant

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Zero Dependencies](https://img.shields.io/badge/Dependencies-Zero-brightgreen.svg)]()
[![Conventional Commits](https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg)](https://conventionalcommits.org)

[简体中文](#简体中文) | [繁體中文](#繁體中文) | [English](#english)

</div>

---

## 简体中文

### 🎉 项目介绍

GitPulse是一款**轻量级、零依赖**的Python CLI工具，专为提升开发者Git工作流效率而设计。它集成了先进的AI能力，能够智能分析代码变更，自动生成符合[Conventional Commits](https://www.conventionalcommits.org/)规范的提交信息，推荐合适的分支名称，提供工作流指导，并自动生成Pull Request描述。

**灵感来源**：在观察了OpenAI Codex CLI、GitHub Copilot CLI等AI编码助手的发展趋势后，我们发现Git工作流自动化仍存在巨大优化空间。GitPulse专注于解决开发者在日常Git操作中遇到的痛点，提供开箱即用的智能辅助。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🤖 **AI智能提交** | 基于代码变更自动生成符合Conventional Commits规范的提交信息 |
| 🌿 **分支建议** | 智能分析变更内容，推荐符合团队规范的分支名称 |
| 🔄 **工作流指导** | 根据当前仓库状态，智能推荐最佳Git操作流程 |
| 📝 **PR自动化** | 自动生成结构清晰、内容完整的Pull Request描述 |
| ✅ **规范验证** | 验证提交信息是否符合Conventional Commits规范 |
| 🔌 **多AI后端** | 支持OpenAI、Anthropic Claude、OpenRouter、Ollama等多种AI提供商 |
| 🎯 **零依赖** | 纯Python标准库实现，无需安装任何额外依赖 |
| 🌍 **多语言** | 支持简体中文、繁體中文、English |

### 🚀 快速开始

#### 环境要求

- Python 3.8 或更高版本
- Git 2.20 或更高版本

#### 安装

```bash
# 使用pip安装
pip install gitpulse

# 或使用缩写命令
gp --help
```

#### 初始化配置

```bash
# 运行初始化向导
gitpulse setup
```

#### 基本使用

```bash
# 查看Git状态概览
gitpulse status

# 获取智能提交建议
gitpulse suggest

# 获取分支名称建议
gitpulse branch

# 获取工作流建议
gitpulse workflow

# 生成PR描述
gitpulse pr

# 验证提交信息
gitpulse validate "feat(auth): add user login"
```

### 📖 详细使用指南

#### 配置AI提供商

GitPulse支持多种AI提供商，您可以根据需求选择：

```bash
# 配置OpenAI
gitpulse config --set-provider openai
export OPENAI_API_KEY=your_key_here

# 配置Anthropic Claude
gitpulse config --set-provider anthropic
export ANTHROPIC_API_KEY=your_key_here

# 配置OpenRouter（免费选项）
gitpulse config --set-provider openrouter
export OPENROUTER_API_KEY=your_key_here

# 配置Ollama（本地模型）
gitpulse config --set-provider ollama
# 无需API密钥，需要本地运行Ollama服务
```

#### 提交规范指南

GitPulse遵循[Conventional Commits](https://www.conventionalcommits.org/)规范：

| 类型 | 描述 | 示例 |
|------|------|------|
| `feat` | ✨ 新功能 | `feat(auth): add OAuth2 login` |
| `fix` | 🐛 修复 | `fix(api): resolve null pointer` |
| `docs` | 📚 文档 | `docs(readme): update install guide` |
| `style` | 💎 格式 | `style(css): fix indentation` |
| `refactor` | 🔨 重构 | `refactor(db): optimize queries` |
| `perf` | ⚡ 性能 | `perf(cache): improve hit rate` |
| `test` | 🧪 测试 | `test(auth): add unit tests` |
| `chore` | 🔧 构建 | `chore(deps): update packages` |

#### 分支命名规范

```
feature/*     - 新功能开发 (例: feature/user-auth)
fix/*         - Bug修复 (例: fix/login-error)
hotfix/*      - 紧急修复 (例: hotfix/security-patch)
docs/*        - 文档更新 (例: docs/api-guide)
refactor/*    - 代码重构 (例: refactor/database-layer)
test/*        - 测试相关 (例: test/unit-coverage)
chore/*       - 构建/工具 (例: chore/update-deps)
release/*     - 发布准备 (例: release/v1.2.0)
```

### 💡 设计思路

GitPulse的设计理念是**简单、智能、无侵入**：

1. **零依赖设计**：仅使用Python标准库，避免依赖冲突和安装问题
2. **多AI后端支持**：不绑定特定AI服务，用户可自由选择
3. **渐进式增强**：基础功能无需AI，AI功能按需启用
4. **团队规范友好**：支持自定义提交规范和分支命名规则

### 📦 打包与部署

```bash
# 本地安装
git clone https://github.com/gitstq/GitPulse.git
cd GitPulse
pip install -e .

# 构建分发包
make build

# 运行测试
make test

# 代码格式化
make format
```

### 🤝 贡献指南

我们欢迎所有形式的贡献！请遵循以下规范：

1. **提交规范**：使用Conventional Commits格式
2. **代码风格**：遵循PEP 8规范
3. **测试覆盖**：新功能需包含单元测试
4. **文档更新**：同步更新README和文档

### 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议。

---

## 繁體中文

### 🎉 專案介紹

GitPulse是一款**輕量級、零依賴**的Python CLI工具，專為提升開發者Git工作流效率而設計。它整合了先進的AI能力，能夠智慧分析程式碼變更，自動生成符合[Conventional Commits](https://www.conventionalcommits.org/)規範的提交資訊，推薦合適的分支名稱，提供工作流指導，並自動生成Pull Request描述。

### ✨ 核心特性

| 特性 | 描述 |
|------|------|
| 🤖 **AI智慧提交** | 基於程式碼變更自動生成符合Conventional Commits規範的提交資訊 |
| 🌿 **分支建議** | 智慧分析變更內容，推薦符合團隊規範的分支名稱 |
| 🔄 **工作流指導** | 根據當前倉庫狀態，智慧推薦最佳Git操作流程 |
| 📝 **PR自動化** | 自動生成結構清晰、內容完整的Pull Request描述 |
| ✅ **規範驗證** | 驗證提交資訊是否符合Conventional Commits規範 |
| 🔌 **多AI後端** | 支援OpenAI、Anthropic Claude、OpenRouter、Ollama等多種AI提供商 |
| 🎯 **零依賴** | 純Python標準庫實現，無需安裝任何額外依賴 |

### 🚀 快速開始

#### 安裝

```bash
pip install gitpulse
```

#### 基本使用

```bash
# 查看Git狀態概覽
gitpulse status

# 獲取智慧提交建議
gitpulse suggest

# 獲取分支名稱建議
gitpulse branch
```

### 📄 開源協議

[MIT License](LICENSE)

---

## English

### 🎉 Introduction

GitPulse is a **lightweight, zero-dependency** Python CLI tool designed to enhance developer productivity in Git workflows. It integrates advanced AI capabilities to intelligently analyze code changes, automatically generate commit messages following the [Conventional Commits](https://www.conventionalcommits.org/) specification, recommend appropriate branch names, provide workflow guidance, and auto-generate Pull Request descriptions.

**Inspiration**: After observing the development trends of AI coding assistants like OpenAI Codex CLI and GitHub Copilot CLI, we identified significant opportunities for optimizing Git workflow automation. GitPulse focuses on solving pain points developers encounter in daily Git operations, providing out-of-the-box intelligent assistance.

### ✨ Core Features

| Feature | Description |
|---------|-------------|
| 🤖 **AI-Powered Commits** | Auto-generate Conventional Commits compliant messages based on code changes |
| 🌿 **Branch Suggestions** | Intelligently analyze changes and recommend team-compliant branch names |
| 🔄 **Workflow Guidance** | Smart recommendations for optimal Git workflows based on repository state |
| 📝 **PR Automation** | Auto-generate well-structured and comprehensive Pull Request descriptions |
| ✅ **Convention Validation** | Validate commit messages against Conventional Commits specification |
| 🔌 **Multi-AI Backends** | Support for OpenAI, Anthropic Claude, OpenRouter, Ollama, and more |
| 🎯 **Zero Dependencies** | Pure Python standard library implementation, no extra dependencies |
| 🌍 **Multi-Language** | Support for 简体中文, 繁體中文, and English |

### 🚀 Quick Start

#### Requirements

- Python 3.8 or higher
- Git 2.20 or higher

#### Installation

```bash
pip install gitpulse
```

#### Basic Usage

```bash
# View Git status overview
gitpulse status

# Get intelligent commit suggestions
gitpulse suggest

# Get branch name suggestions
gitpulse branch

# Get workflow recommendations
gitpulse workflow

# Generate PR description
gitpulse pr

# Validate commit message
gitpulse validate "feat(auth): add user login"
```

### 📖 Detailed Usage

#### Configure AI Provider

```bash
# Configure OpenAI
gitpulse config --set-provider openai
export OPENAI_API_KEY=your_key_here

# Configure Anthropic Claude
gitpulse config --set-provider anthropic
export ANTHROPIC_API_KEY=your_key_here

# Configure OpenRouter (free tier available)
gitpulse config --set-provider openrouter
export OPENROUTER_API_KEY=your_key_here

# Configure Ollama (local models)
gitpulse config --set-provider ollama
# No API key needed, requires local Ollama service
```

#### Commit Convention Guide

GitPulse follows the [Conventional Commits](https://www.conventionalcommits.org/) specification:

| Type | Description | Example |
|------|-------------|---------|
| `feat` | ✨ New feature | `feat(auth): add OAuth2 login` |
| `fix` | 🐛 Bug fix | `fix(api): resolve null pointer` |
| `docs` | 📚 Documentation | `docs(readme): update install guide` |
| `style` | 💎 Code style | `style(css): fix indentation` |
| `refactor` | 🔨 Refactoring | `refactor(db): optimize queries` |
| `perf` | ⚡ Performance | `perf(cache): improve hit rate` |
| `test` | 🧪 Testing | `test(auth): add unit tests` |
| `chore` | 🔧 Build/tooling | `chore(deps): update packages` |

### 💡 Design Philosophy

GitPulse is designed with **simplicity, intelligence, and non-intrusiveness** in mind:

1. **Zero Dependencies**: Uses only Python standard library to avoid dependency conflicts
2. **Multi-AI Backend Support**: Not tied to any specific AI service, freedom of choice
3. **Progressive Enhancement**: Core features work without AI, AI features are opt-in
4. **Team-Friendly**: Supports custom commit conventions and branch naming rules

### 📦 Packaging & Deployment

```bash
# Local installation
git clone https://github.com/gitstq/GitPulse.git
cd GitPulse
pip install -e .

# Build distribution
make build

# Run tests
make test

# Code formatting
make format
```

### 🤝 Contributing

We welcome all forms of contributions! Please follow these guidelines:

1. **Commit Convention**: Use Conventional Commits format
2. **Code Style**: Follow PEP 8 guidelines
3. **Test Coverage**: Include unit tests for new features
4. **Documentation**: Update README and docs accordingly

### 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<div align="center">

**Made with ❤️ by GitPulse Team**

[Report Bug](https://github.com/gitstq/GitPulse/issues) · [Request Feature](https://github.com/gitstq/GitPulse/issues) · [View Source](https://github.com/gitstq/GitPulse)

</div>

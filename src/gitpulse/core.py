"""
GitPulse核心模块 - 主控制器，整合所有功能
"""

import os
import sys
import json
from typing import Dict, List, Optional
from dataclasses import asdict

from .git_analyzer import GitAnalyzer, ChangeType
from .ai_engine import AIEngine, AIConfig, AIProvider
from .workflow import WorkflowManager, WorkflowType


class GitPulse:
    """GitPulse主类"""
    
    def __init__(self, repo_path: str = ".", config_path: Optional[str] = None):
        self.repo_path = repo_path
        self.config_path = config_path or os.path.expanduser("~/.gitpulse/config.json")
        
        # 初始化组件
        self.git = GitAnalyzer(repo_path)
        self.workflow = WorkflowManager()
        self.ai: Optional[AIEngine] = None
        
        # 加载配置
        self.config = self._load_config()
        self._init_ai_engine()
    
    def _load_config(self) -> Dict:
        """加载配置"""
        default_config = {
            "ai_provider": "openrouter",
            "model": None,
            "temperature": 0.3,
            "max_tokens": 500,
            "auto_commit": False,
            "commit_template": "conventional",
            "language": "zh"
        }
        
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded_config = json.load(f)
                    default_config.update(loaded_config)
            except Exception:
                pass
        
        # 从环境变量读取API密钥
        env_keys = {
            "openai": "OPENAI_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY",
            "openrouter": "OPENROUTER_API_KEY",
            "ollama": None
        }
        
        provider = default_config.get("ai_provider", "openrouter")
        env_key = env_keys.get(provider)
        
        if env_key:
            default_config["api_key"] = os.environ.get(env_key, "")
        
        return default_config
    
    def _save_config(self):
        """保存配置"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        config_to_save = {k: v for k, v in self.config.items() if k != "api_key"}
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(config_to_save, f, indent=2, ensure_ascii=False)
    
    def _init_ai_engine(self):
        """初始化AI引擎"""
        provider_str = self.config.get("ai_provider", "openrouter")
        api_key = self.config.get("api_key", "")
        
        if not api_key and provider_str != "ollama":
            return
        
        try:
            ai_config = AIConfig(
                provider=AIProvider(provider_str),
                api_key=api_key,
                model=self.config.get("model"),
                temperature=self.config.get("temperature", 0.3),
                max_tokens=self.config.get("max_tokens", 500)
            )
            self.ai = AIEngine(ai_config)
        except Exception:
            self.ai = None
    
    def status(self) -> Dict:
        """获取Git状态概览"""
        git_status = self.git.get_status()
        
        return {
            "branch": git_status.branch,
            "ahead": git_status.ahead,
            "behind": git_status.behind,
            "staged_count": len(git_status.staged),
            "unstaged_count": len(git_status.unstaged),
            "untracked_count": len(git_status.untracked),
            "is_clean": git_status.is_clean,
            "staged_files": [f.path for f in git_status.staged],
            "unstaged_files": [f.path for f in git_status.unstaged],
            "untracked_files": git_status.untracked
        }
    
    def suggest_commit(self, use_ai: bool = True) -> Dict:
        """建议提交信息"""
        git_status = self.git.get_status()
        
        if git_status.is_clean:
            return {
                "success": False,
                "message": "没有可提交的变更",
                "suggestions": []
            }
        
        diff = self.git.get_diff(staged=True)
        analysis = self.git.analyze_changes()
        
        suggestions = []
        
        if use_ai and self.ai:
            try:
                context = {
                    "analysis": analysis,
                    "branch": git_status.branch
                }
                ai_message = self.ai.generate_commit_message(diff, context)
                parsed = AIEngine.parse_commit_message(ai_message)
                suggestions.append({
                    "type": "ai",
                    "message": ai_message,
                    "parsed": parsed
                })
            except Exception as e:
                suggestions.append({
                    "type": "ai",
                    "message": f"AI生成失败: {str(e)}",
                    "parsed": None
                })
        
        # 基于规则的生成
        rule_based = self._generate_rule_based_commit(analysis, git_status)
        suggestions.append({
            "type": "rule",
            "message": rule_based,
            "parsed": AIEngine.parse_commit_message(rule_based)
        })
        
        return {
            "success": True,
            "diff_summary": {
                "files_changed": analysis["total_files"],
                "insertions": analysis["total_insertions"],
                "deletions": analysis["total_deletions"]
            },
            "suggestions": suggestions
        }
    
    def _generate_rule_based_commit(self, analysis: Dict, status) -> str:
        """基于规则生成提交信息"""
        categories = analysis.get("change_categories", {})
        
        # 确定提交类型
        if categories.get("test_changes", 0) > 0 and categories.get("code_changes", 0) == 0:
            commit_type = "test"
        elif categories.get("doc_changes", 0) > categories.get("code_changes", 0):
            commit_type = "docs"
        elif categories.get("config_changes", 0) > 0 and analysis["total_files"] <= 3:
            commit_type = "chore"
        else:
            commit_type = "feat" if analysis["total_insertions"] > analysis["total_deletions"] else "update"
        
        # 生成描述
        file_types = analysis.get("file_types", {})
        if file_types:
            main_type = max(file_types.items(), key=lambda x: x[1])[0]
            if main_type in ["py", "js", "ts", "java", "go"]:
                scope = "code"
            elif main_type in ["md", "rst", "txt"]:
                scope = "docs"
            elif main_type in ["json", "yml", "yaml", "toml"]:
                scope = "config"
            else:
                scope = main_type
        else:
            scope = ""
        
        # 生成subject
        if analysis["total_files"] == 1:
            subject = f"update {list(file_types.keys())[0] if file_types else 'file'}"
        else:
            subject = f"update {analysis['total_files']} files"
        
        if scope:
            return f"{commit_type}({scope}): {subject}"
        else:
            return f"{commit_type}: {subject}"
    
    def suggest_branch(self) -> Dict:
        """建议分支名称"""
        suggestions = self.git.get_branch_suggestions()
        
        return {
            "success": True,
            "suggestions": suggestions,
            "naming_guide": self.workflow.get_branch_naming_guide()
        }
    
    def suggest_workflow(self) -> Dict:
        """建议工作流"""
        status = self.git.get_status()
        analysis = self.git.analyze_changes()
        
        # 推荐工作流类型
        workflow_type = self.workflow.suggest_workflow(
            {"staged": len(status.staged), "unstaged": len(status.unstaged)},
            analysis
        )
        
        workflow = self.workflow.get_workflow(workflow_type)
        checklist = self.workflow.generate_checklist(workflow_type)
        
        # 获取AI建议
        ai_suggestions = []
        if self.ai:
            try:
                history = [c.message for c in self.git.get_recent_commits(3)]
                ai_suggestions = self.ai.suggest_workflow(
                    {"branch": status.branch, "is_clean": status.is_clean},
                    history
                )
            except Exception:
                pass
        
        return {
            "success": True,
            "recommended_workflow": workflow_type.value,
            "workflow_name": workflow.name if workflow else "",
            "description": workflow.description if workflow else "",
            "checklist": checklist,
            "ai_suggestions": ai_suggestions
        }
    
    def validate_commit(self, message: str) -> Dict:
        """验证提交信息"""
        result = self.workflow.validate_commit_message(message)
        
        return {
            "valid": result["valid"],
            "errors": result["errors"],
            "warnings": result["warnings"],
            "suggestions": result["suggestions"],
            "convention_guide": self.workflow.get_commit_convention()
        }
    
    def generate_pr(self, base_branch: str = "main") -> Dict:
        """生成PR描述"""
        commits = self.git.get_recent_commits(10)
        analysis = self.git.analyze_changes()
        
        commit_messages = [c.message for c in commits]
        diff_summary = f"""
Files changed: {analysis['total_files']}
Insertions: {analysis['total_insertions']}
Deletions: {analysis['total_deletions']}
"""
        
        if self.ai:
            try:
                pr_description = self.ai.generate_pr_description(commit_messages, diff_summary)
            except Exception as e:
                pr_description = f"AI生成失败，请手动编写。错误: {str(e)}"
        else:
            pr_description = self._generate_default_pr_description(commit_messages, analysis)
        
        return {
            "success": True,
            "title": f"Merge changes to {base_branch}",
            "description": pr_description,
            "commits": commit_messages[:5],
            "stats": {
                "files_changed": analysis["total_files"],
                "insertions": analysis["total_insertions"],
                "deletions": analysis["total_deletions"]
            }
        }
    
    def _generate_default_pr_description(self, commits: List[str], analysis: Dict) -> str:
        """生成默认PR描述"""
        commits_text = "\n".join([f"- {c}" for c in commits[:5]])
        
        return f"""## 变更内容

### 提交记录
{commits_text}

### 统计
- 文件变更: {analysis['total_files']}
- 新增行数: {analysis['total_insertions']}
- 删除行数: {analysis['total_deletions']}

### 检查清单
- [ ] 代码已自测
- [ ] 文档已更新
- [ ] 测试已通过
"""
    
    def config(self, key: Optional[str] = None, value: Optional[str] = None) -> Dict:
        """配置管理"""
        if key is None:
            # 显示所有配置
            return {
                "success": True,
                "config_path": self.config_path,
                "config": {k: v for k, v in self.config.items() if k != "api_key"}
            }
        
        if value is None:
            # 获取特定配置
            return {
                "success": True,
                "key": key,
                "value": self.config.get(key)
            }
        
        # 设置配置
        self.config[key] = value
        self._save_config()
        
        # 重新初始化AI引擎
        if key in ["ai_provider", "model", "temperature", "max_tokens"]:
            self._init_ai_engine()
        
        return {
            "success": True,
            "message": f"配置已更新: {key} = {value}"
        }

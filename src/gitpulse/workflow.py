"""
工作流管理器 - 提供智能Git工作流建议和自动化
"""

import json
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum


class WorkflowType(Enum):
    """工作流类型"""
    FEATURE = "feature"  # 功能开发
    HOTFIX = "hotfix"    # 热修复
    RELEASE = "release"  # 发布
    DOCS = "docs"        # 文档更新
    REFACTOR = "refactor"  # 重构


@dataclass
class WorkflowStep:
    """工作流步骤"""
    order: int
    command: str
    description: str
    is_optional: bool = False
    verification: Optional[str] = None


@dataclass
class Workflow:
    """工作流定义"""
    name: str
    type: WorkflowType
    description: str
    steps: List[WorkflowStep]
    prerequisites: List[str]


class WorkflowManager:
    """工作流管理器"""
    
    # 预定义工作流模板
    WORKFLOW_TEMPLATES = {
        WorkflowType.FEATURE: Workflow(
            name="功能开发工作流",
            type=WorkflowType.FEATURE,
            description="标准的功能开发分支工作流",
            prerequisites=["确保基于最新的main分支", "确认相关Issue已创建"],
            steps=[
                WorkflowStep(1, "git checkout main", "切换到主分支"),
                WorkflowStep(2, "git pull origin main", "拉取最新代码"),
                WorkflowStep(3, "git checkout -b feature/<name>", "创建功能分支"),
                WorkflowStep(4, "# 进行开发工作", "开发功能", is_optional=True),
                WorkflowStep(5, "git add .", "暂存变更"),
                WorkflowStep(6, "git commit -m 'feat: xxx'", "提交变更"),
                WorkflowStep(7, "git push -u origin feature/<name>", "推送到远程"),
                WorkflowStep(8, "# 创建Pull Request", "创建PR", is_optional=True),
            ]
        ),
        WorkflowType.HOTFIX: Workflow(
            name="热修复工作流",
            type=WorkflowType.HOTFIX,
            description="紧急修复生产问题",
            prerequisites=["确认问题严重性", "通知相关团队成员"],
            steps=[
                WorkflowStep(1, "git checkout main", "切换到主分支"),
                WorkflowStep(2, "git pull origin main", "拉取最新代码"),
                WorkflowStep(3, "git checkout -b hotfix/<name>", "创建热修复分支"),
                WorkflowStep(4, "# 快速修复", "修复问题", is_optional=True),
                WorkflowStep(5, "git add .", "暂存变更"),
                WorkflowStep(6, "git commit -m 'fix: xxx'", "提交修复"),
                WorkflowStep(7, "git push -u origin hotfix/<name>", "推送到远程"),
                WorkflowStep(8, "# 快速审核并合并", "紧急合并", is_optional=True),
            ]
        ),
        WorkflowType.RELEASE: Workflow(
            name="发布工作流",
            type=WorkflowType.RELEASE,
            description="版本发布流程",
            prerequisites=["所有功能已完成并合并", "版本号已确定", "CHANGELOG已更新"],
            steps=[
                WorkflowStep(1, "git checkout main", "切换到主分支"),
                WorkflowStep(2, "git pull origin main", "拉取最新代码"),
                WorkflowStep(3, "git tag -a v<version> -m 'Release v<version>'", "创建标签"),
                WorkflowStep(4, "git push origin v<version>", "推送标签"),
                WorkflowStep(5, "# 创建GitHub Release", "创建Release", is_optional=True),
            ]
        ),
        WorkflowType.DOCS: Workflow(
            name="文档更新工作流",
            type=WorkflowType.DOCS,
            description="文档和README更新",
            prerequisites=["确认文档变更范围"],
            steps=[
                WorkflowStep(1, "git checkout main", "切换到主分支"),
                WorkflowStep(2, "git pull origin main", "拉取最新代码"),
                WorkflowStep(3, "git checkout -b docs/<name>", "创建文档分支"),
                WorkflowStep(4, "# 更新文档", "编辑文档", is_optional=True),
                WorkflowStep(5, "git add .", "暂存变更"),
                WorkflowStep(6, "git commit -m 'docs: xxx'", "提交文档"),
                WorkflowStep(7, "git push -u origin docs/<name>", "推送到远程"),
            ]
        ),
        WorkflowType.REFACTOR: Workflow(
            name="重构工作流",
            type=WorkflowType.REFACTOR,
            description="代码重构流程",
            prerequisites=["确保测试覆盖充分", "备份重要数据"],
            steps=[
                WorkflowStep(1, "git checkout main", "切换到主分支"),
                WorkflowStep(2, "git pull origin main", "拉取最新代码"),
                WorkflowStep(3, "git checkout -b refactor/<name>", "创建重构分支"),
                WorkflowStep(4, "# 执行重构", "重构代码", is_optional=True),
                WorkflowStep(5, "# 运行测试", "验证重构", is_optional=True),
                WorkflowStep(6, "git add .", "暂存变更"),
                WorkflowStep(7, "git commit -m 'refactor: xxx'", "提交重构"),
                WorkflowStep(8, "git push -u origin refactor/<name>", "推送到远程"),
            ]
        ),
    }
    
    def __init__(self):
        self.custom_workflows: Dict[str, Workflow] = {}
    
    def get_workflow(self, workflow_type: WorkflowType) -> Workflow:
        """获取工作流模板"""
        return self.WORKFLOW_TEMPLATES.get(workflow_type)
    
    def suggest_workflow(self, git_status: Dict, change_analysis: Dict) -> WorkflowType:
        """基于当前状态推荐工作流"""
        # 分析变更内容
        categories = change_analysis.get("change_categories", {})
        
        # 根据变更类型推荐工作流
        if categories.get("doc_changes", 0) > categories.get("code_changes", 0):
            return WorkflowType.DOCS
        
        # 检查是否为修复
        diff = git_status.get("diff", "").lower()
        if any(kw in diff for kw in ["fix", "bug", "repair", "correct", "error"]):
            return WorkflowType.HOTFIX
        
        # 检查是否为重构
        if any(kw in diff for kw in ["refactor", "restructure", "clean", "simplify"]):
            return WorkflowType.REFACTOR
        
        # 默认为功能开发
        return WorkflowType.FEATURE
    
    def generate_checklist(self, workflow_type: WorkflowType) -> List[str]:
        """生成工作流检查清单"""
        workflow = self.WORKFLOW_TEMPLATES.get(workflow_type)
        if not workflow:
            return []
        
        checklist = []
        
        # 前置条件
        for prereq in workflow.prerequisites:
            checklist.append(f"[ ] {prereq}")
        
        # 步骤检查
        for step in workflow.steps:
            if not step.is_optional:
                checklist.append(f"[ ] {step.description}")
        
        return checklist
    
    def get_branch_naming_guide(self) -> Dict[str, str]:
        """获取分支命名规范"""
        return {
            "feature/*": "新功能开发 (例: feature/user-auth)",
            "fix/*": "Bug修复 (例: fix/login-error)",
            "hotfix/*": "紧急修复 (例: hotfix/security-patch)",
            "docs/*": "文档更新 (例: docs/api-guide)",
            "refactor/*": "代码重构 (例: refactor/database-layer)",
            "test/*": "测试相关 (例: test/unit-coverage)",
            "chore/*": "构建/工具 (例: chore/update-deps)",
            "release/*": "发布准备 (例: release/v1.2.0)",
        }
    
    def get_commit_convention(self) -> Dict[str, str]:
        """获取提交规范"""
        return {
            "feat": "✨ 新功能 (feature)",
            "fix": "🐛 修复 (bug fix)",
            "docs": "📚 文档 (documentation)",
            "style": "💎 格式 (formatting)",
            "refactor": "🔨 重构 (refactoring)",
            "perf": "⚡ 性能 (performance)",
            "test": "🧪 测试 (testing)",
            "chore": "🔧 构建 (build/tooling)",
            "ci": "🚀 CI/CD (continuous integration)",
            "revert": "⏪ 回退 (revert)",
        }
    
    def validate_commit_message(self, message: str) -> Dict:
        """验证提交信息是否符合规范"""
        result = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "suggestions": []
        }
        
        lines = message.strip().split("\n")
        if not lines or not lines[0]:
            result["valid"] = False
            result["errors"].append("提交信息不能为空")
            return result
        
        first_line = lines[0]
        
        # 检查长度
        if len(first_line) > 72:
            result["warnings"].append("标题超过72个字符，建议缩短")
        
        # 检查Conventional Commits格式
        import re
        pattern = r"^(\w+)(?:\(([^)]+)\))?:\s*(.+)$"
        match = re.match(pattern, first_line)
        
        if not match:
            result["warnings"].append("未使用Conventional Commits格式")
            result["suggestions"].append("建议使用: type(scope): subject 格式")
        else:
            commit_type = match.group(1)
            valid_types = self.get_commit_convention().keys()
            
            if commit_type not in valid_types:
                result["warnings"].append(f"未知的提交类型: {commit_type}")
                result["suggestions"].append(f"建议使用: {', '.join(valid_types)}")
            
            subject = match.group(3)
            if subject[0].isupper():
                result["warnings"].append("subject首字母应小写")
            
            if subject.endswith("."):
                result["warnings"].append("subject不应以句号结尾")
        
        # 检查body和footer
        if len(lines) > 1:
            # 检查是否有空行分隔
            if lines[1].strip():
                result["warnings"].append("标题和正文之间应有空行")
        
        return result
    
    def create_custom_workflow(self, name: str, workflow_type: str, 
                               steps: List[Dict], prerequisites: List[str]) -> Workflow:
        """创建自定义工作流"""
        workflow_steps = []
        for i, step_data in enumerate(steps, 1):
            workflow_steps.append(WorkflowStep(
                order=i,
                command=step_data.get("command", ""),
                description=step_data.get("description", ""),
                is_optional=step_data.get("is_optional", False),
                verification=step_data.get("verification")
            ))
        
        workflow = Workflow(
            name=name,
            type=WorkflowType(workflow_type),
            description=f"自定义工作流: {name}",
            steps=workflow_steps,
            prerequisites=prerequisites
        )
        
        self.custom_workflows[name] = workflow
        return workflow
    
    def export_workflow(self, workflow_type: WorkflowType) -> str:
        """导出工作流为JSON"""
        workflow = self.WORKFLOW_TEMPLATES.get(workflow_type)
        if not workflow:
            return "{}"
        
        data = {
            "name": workflow.name,
            "type": workflow.type.value,
            "description": workflow.description,
            "prerequisites": workflow.prerequisites,
            "steps": [
                {
                    "order": s.order,
                    "command": s.command,
                    "description": s.description,
                    "is_optional": s.is_optional,
                    "verification": s.verification
                }
                for s in workflow.steps
            ]
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)

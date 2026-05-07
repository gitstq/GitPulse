"""
GitPulse - AI驱动的Git工作流智能助手
AI-Powered Git Workflow Intelligence Assistant

一个轻量级、零依赖的CLI工具，为开发者提供智能Git工作流辅助，
包括智能提交信息生成、分支管理建议、PR自动化等功能。
"""

__version__ = "1.0.0"
__author__ = "GitPulse Team"
__license__ = "MIT"

from .core import GitPulse
from .git_analyzer import GitAnalyzer
from .ai_engine import AIEngine
from .workflow import WorkflowManager

__all__ = ["GitPulse", "GitAnalyzer", "AIEngine", "WorkflowManager"]

"""
Git仓库分析器 - 提供Git状态检测、差异分析、历史追踪等功能
"""

import subprocess
import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class ChangeType(Enum):
    """变更类型枚举"""
    ADDED = "A"
    MODIFIED = "M"
    DELETED = "D"
    RENAMED = "R"
    COPIED = "C"
    UNTRACKED = "?"


@dataclass
class FileChange:
    """文件变更数据类"""
    path: str
    change_type: ChangeType
    insertions: int = 0
    deletions: int = 0
    old_path: Optional[str] = None


@dataclass
class GitStatus:
    """Git状态数据类"""
    branch: str
    ahead: int
    behind: int
    staged: List[FileChange]
    unstaged: List[FileChange]
    untracked: List[str]
    is_clean: bool


@dataclass
class CommitInfo:
    """提交信息数据类"""
    hash: str
    short_hash: str
    author: str
    email: str
    date: str
    message: str
    files_changed: int
    insertions: int
    deletions: int


class GitAnalyzer:
    """Git仓库分析器"""
    
    def __init__(self, repo_path: str = "."):
        self.repo_path = repo_path
        self._check_git_repo()
    
    def _run_git_command(self, args: List[str], check: bool = True) -> Tuple[int, str, str]:
        """执行Git命令"""
        try:
            result = subprocess.run(
                ["git"] + args,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=check
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.CalledProcessError as e:
            if check:
                raise
            return e.returncode, e.stdout, e.stderr
        except FileNotFoundError:
            raise RuntimeError("Git未安装或不在PATH中")
    
    def _check_git_repo(self):
        """检查是否为Git仓库"""
        returncode, _, _ = self._run_git_command(
            ["rev-parse", "--git-dir"], 
            check=False
        )
        if returncode != 0:
            raise ValueError(f"'{self.repo_path}' 不是有效的Git仓库")
    
    def get_status(self) -> GitStatus:
        """获取Git状态"""
        # 获取分支信息
        _, branch_output, _ = self._run_git_command(["branch", "--show-current"])
        branch = branch_output.strip()
        
        # 获取ahead/behind信息
        _, ahead_behind, _ = self._run_git_command(
            ["rev-list", "--left-right", "--count", f"HEAD...origin/{branch}"],
            check=False
        )
        ahead, behind = 0, 0
        if ahead_behind:
            parts = ahead_behind.strip().split("\t")
            if len(parts) == 2:
                ahead, behind = int(parts[0]), int(parts[1])
        
        # 获取状态
        _, status_output, _ = self._run_git_command(
            ["status", "--porcelain", "-u"]
        )
        
        staged = []
        unstaged = []
        untracked = []
        
        for line in status_output.strip().split("\n"):
            if not line:
                continue
            
            index_status = line[0] if len(line) > 0 else " "
            worktree_status = line[1] if len(line) > 1 else " "
            file_path = line[3:].strip() if len(line) > 3 else ""
            
            if index_status == "?":
                untracked.append(file_path)
            elif index_status != " ":
                # 已暂存
                change_type = self._parse_change_type(index_status)
                staged.append(FileChange(path=file_path, change_type=change_type))
            
            if worktree_status != " " and worktree_status != "?":
                # 未暂存
                change_type = self._parse_change_type(worktree_status)
                unstaged.append(FileChange(path=file_path, change_type=change_type))
        
        is_clean = len(staged) == 0 and len(unstaged) == 0 and len(untracked) == 0
        
        return GitStatus(
            branch=branch,
            ahead=ahead,
            behind=behind,
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            is_clean=is_clean
        )
    
    def _parse_change_type(self, status: str) -> ChangeType:
        """解析变更类型"""
        mapping = {
            "A": ChangeType.ADDED,
            "M": ChangeType.MODIFIED,
            "D": ChangeType.DELETED,
            "R": ChangeType.RENAMED,
            "C": ChangeType.COPIED,
            "?": ChangeType.UNTRACKED,
        }
        return mapping.get(status, ChangeType.MODIFIED)
    
    def get_diff(self, staged: bool = True, file_path: Optional[str] = None) -> str:
        """获取差异内容"""
        args = ["diff", "--no-color"]
        if staged:
            args.append("--staged")
        if file_path:
            args.append(file_path)
        
        _, output, _ = self._run_git_command(args)
        return output
    
    def get_diff_stats(self, staged: bool = True) -> Dict[str, Tuple[int, int]]:
        """获取差异统计信息"""
        args = ["diff", "--numstat"]
        if staged:
            args.append("--staged")
        
        _, output, _ = self._run_git_command(args)
        
        stats = {}
        for line in output.strip().split("\n"):
            if not line or line.startswith("-"):
                continue
            parts = line.split("\t")
            if len(parts) >= 3:
                insertions = int(parts[0]) if parts[0].isdigit() else 0
                deletions = int(parts[1]) if parts[1].isdigit() else 0
                file_path = parts[2]
                stats[file_path] = (insertions, deletions)
        
        return stats
    
    def get_recent_commits(self, count: int = 5) -> List[CommitInfo]:
        """获取最近提交"""
        format_str = "%H|%h|%an|%ae|%ad|%s"
        _, output, _ = self._run_git_command([
            "log", f"-{count}", f"--pretty=format:{format_str}"
        ])
        
        commits = []
        for line in output.strip().split("\n"):
            if not line:
                continue
            parts = line.split("|", 5)
            if len(parts) >= 6:
                commits.append(CommitInfo(
                    hash=parts[0],
                    short_hash=parts[1],
                    author=parts[2],
                    email=parts[3],
                    date=parts[4],
                    message=parts[5],
                    files_changed=0,
                    insertions=0,
                    deletions=0
                ))
        
        return commits
    
    def get_branch_suggestions(self) -> List[str]:
        """获取分支建议"""
        # 获取当前分支
        status = self.get_status()
        current = status.branch
        
        suggestions = []
        
        # 基于变更内容生成分支名建议
        diff = self.get_diff(staged=True)
        
        # 检测文件类型
        file_types = set()
        for line in diff.split("\n"):
            if line.startswith("diff --git"):
                file_path = line.split(" ")[2][2:]  # 去掉 b/
                ext = file_path.split(".")[-1] if "." in file_path else ""
                if ext:
                    file_types.add(ext)
        
        # 检测变更类型
        has_feature = any(kw in diff.lower() for kw in ["add", "new", "feature", "implement"])
        has_fix = any(kw in diff.lower() for kw in ["fix", "bug", "repair", "correct"])
        has_refactor = any(kw in diff.lower() for kw in ["refactor", "restructure", "clean"])
        
        # 生成分支名前缀
        prefix = ""
        if has_feature:
            prefix = "feature"
        elif has_fix:
            prefix = "fix"
        elif has_refactor:
            prefix = "refactor"
        else:
            prefix = "update"
        
        # 基于文件类型生成描述
        if file_types:
            type_desc = "-".join(sorted(file_types))[:20]
            suggestions.append(f"{prefix}/{type_desc}")
        
        # 基于时间戳
        import datetime
        timestamp = datetime.datetime.now().strftime("%m%d")
        suggestions.append(f"{prefix}/update-{timestamp}")
        
        # 简单描述
        suggestions.append(f"{prefix}/code-changes")
        
        return suggestions[:3]
    
    def analyze_changes(self) -> Dict:
        """深度分析变更内容"""
        diff = self.get_diff(staged=True)
        stats = self.get_diff_stats(staged=True)
        
        analysis = {
            "total_files": len(stats),
            "total_insertions": sum(s[0] for s in stats.values()),
            "total_deletions": sum(s[1] for s in stats.values()),
            "file_types": {},
            "change_categories": {
                "code_changes": 0,
                "config_changes": 0,
                "doc_changes": 0,
                "test_changes": 0,
            }
        }
        
        for file_path in stats.keys():
            # 分析文件类型
            ext = file_path.split(".")[-1] if "." in file_path else "no-ext"
            analysis["file_types"][ext] = analysis["file_types"].get(ext, 0) + 1
            
            # 分析变更类别
            if any(file_path.endswith(ext) for ext in [".py", ".js", ".ts", ".java", ".go", ".rs"]):
                analysis["change_categories"]["code_changes"] += 1
            elif any(file_path.endswith(ext) for ext in [".json", ".yml", ".yaml", ".toml", ".ini"]):
                analysis["change_categories"]["config_changes"] += 1
            elif any(file_path.endswith(ext) for ext in [".md", ".rst", ".txt"]):
                analysis["change_categories"]["doc_changes"] += 1
            elif "test" in file_path.lower() or "spec" in file_path.lower():
                analysis["change_categories"]["test_changes"] += 1
        
        return analysis

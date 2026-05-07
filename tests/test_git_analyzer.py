"""
GitAnalyzer单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess

from gitpulse.git_analyzer import GitAnalyzer, ChangeType, GitStatus


class TestGitAnalyzer(unittest.TestCase):
    """测试GitAnalyzer类"""
    
    @patch("gitpulse.git_analyzer.subprocess.run")
    def test_init_valid_repo(self, mock_run):
        """测试初始化有效仓库"""
        mock_run.return_value = MagicMock(returncode=0, stdout=".git", stderr="")
        
        analyzer = GitAnalyzer("/fake/path")
        self.assertEqual(analyzer.repo_path, "/fake/path")
    
    @patch("gitpulse.git_analyzer.subprocess.run")
    def test_init_invalid_repo(self, mock_run):
        """测试初始化无效仓库"""
        mock_run.return_value = MagicMock(returncode=1, stdout="", stderr="")
        
        with self.assertRaises(ValueError):
            GitAnalyzer("/not/a/repo")
    
    @patch("gitpulse.git_analyzer.subprocess.run")
    def test_get_status_clean(self, mock_run):
        """测试获取干净状态"""
        def side_effect(*args, **kwargs):
            cmd = args[0]
            mock = MagicMock()
            
            if "branch" in cmd and "show-current" in cmd:
                mock.stdout = "main\n"
                mock.returncode = 0
            elif "rev-list" in cmd:
                mock.stdout = "0\t0\n"
                mock.returncode = 0
            elif "status" in cmd:
                mock.stdout = ""
                mock.returncode = 0
            else:
                mock.stdout = ""
                mock.returncode = 0
            
            return mock
        
        mock_run.side_effect = side_effect
        
        analyzer = GitAnalyzer(".")
        status = analyzer.get_status()
        
        self.assertEqual(status.branch, "main")
        self.assertTrue(status.is_clean)
        self.assertEqual(len(status.staged), 0)
        self.assertEqual(len(status.unstaged), 0)
    
    def test_parse_change_type(self):
        """测试变更类型解析"""
        analyzer = MagicMock()
        analyzer.repo_path = "."
        
        # 使用真实的GitAnalyzer实例来测试私有方法
        with patch.object(GitAnalyzer, "_check_git_repo"):
            ga = GitAnalyzer(".")
            
            self.assertEqual(ga._parse_change_type("A"), ChangeType.ADDED)
            self.assertEqual(ga._parse_change_type("M"), ChangeType.MODIFIED)
            self.assertEqual(ga._parse_change_type("D"), ChangeType.DELETED)
            self.assertEqual(ga._parse_change_type("R"), ChangeType.RENAMED)
            self.assertEqual(ga._parse_change_type("?"), ChangeType.UNTRACKED)


if __name__ == "__main__":
    unittest.main()

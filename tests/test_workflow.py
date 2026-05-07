"""
WorkflowManager单元测试
"""

import unittest

from gitpulse.workflow import WorkflowManager, WorkflowType


class TestWorkflowManager(unittest.TestCase):
    """测试WorkflowManager类"""
    
    def setUp(self):
        """测试前准备"""
        self.manager = WorkflowManager()
    
    def test_get_workflow_feature(self):
        """测试获取功能开发工作流"""
        workflow = self.manager.get_workflow(WorkflowType.FEATURE)
        
        self.assertIsNotNone(workflow)
        self.assertEqual(workflow.type, WorkflowType.FEATURE)
        self.assertEqual(len(workflow.steps) > 0, True)
    
    def test_suggest_workflow_docs(self):
        """测试推荐文档工作流"""
        git_status = {"staged": 2, "unstaged": 0}
        change_analysis = {
            "change_categories": {
                "doc_changes": 5,
                "code_changes": 1
            }
        }
        
        workflow_type = self.manager.suggest_workflow(git_status, change_analysis)
        
        self.assertEqual(workflow_type, WorkflowType.DOCS)
    
    def test_validate_commit_message_valid(self):
        """测试验证有效提交信息"""
        message = "feat(auth): add user login"
        
        result = self.manager.validate_commit_message(message)
        
        self.assertTrue(result["valid"])
        self.assertEqual(len(result["errors"]), 0)
    
    def test_validate_commit_message_empty(self):
        """测试验证空提交信息"""
        message = ""
        
        result = self.manager.validate_commit_message(message)
        
        self.assertFalse(result["valid"])
        self.assertTrue(len(result["errors"]) > 0)
    
    def test_get_branch_naming_guide(self):
        """测试获取分支命名规范"""
        guide = self.manager.get_branch_naming_guide()
        
        self.assertIn("feature/*", guide)
        self.assertIn("fix/*", guide)
        self.assertIn("hotfix/*", guide)
    
    def test_get_commit_convention(self):
        """测试获取提交规范"""
        convention = self.manager.get_commit_convention()
        
        self.assertIn("feat", convention)
        self.assertIn("fix", convention)
        self.assertIn("docs", convention)


if __name__ == "__main__":
    unittest.main()

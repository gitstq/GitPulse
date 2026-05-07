"""
AIEngine单元测试
"""

import unittest
from unittest.mock import patch, MagicMock
import json

from gitpulse.ai_engine import AIEngine, AIConfig, AIProvider


class TestAIEngine(unittest.TestCase):
    """测试AIEngine类"""
    
    def test_init_valid_config(self):
        """测试有效配置初始化"""
        config = AIConfig(
            provider=AIProvider.OPENAI,
            api_key="test-key",
            model="gpt-4"
        )
        
        engine = AIEngine(config)
        self.assertEqual(engine.config.provider, AIProvider.OPENAI)
        self.assertEqual(engine.config.model, "gpt-4")
    
    def test_init_missing_api_key(self):
        """测试缺少API密钥"""
        config = AIConfig(
            provider=AIProvider.OPENAI,
            api_key="",
            model="gpt-4"
        )
        
        with self.assertRaises(ValueError):
            AIEngine(config)
    
    def test_init_ollama_no_key(self):
        """测试Ollama不需要API密钥"""
        config = AIConfig(
            provider=AIProvider.OLLAMA,
            api_key="",
            model="llama3.2"
        )
        
        # 不应抛出异常
        engine = AIEngine(config)
        self.assertEqual(engine.config.provider, AIProvider.OLLAMA)
    
    def test_parse_commit_message_conventional(self):
        """测试解析Conventional Commit格式"""
        message = "feat(auth): add user login"
        
        result = AIEngine.parse_commit_message(message)
        
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], "auth")
        self.assertEqual(result["subject"], "add user login")
    
    def test_parse_commit_message_non_conventional(self):
        """测试解析非标准格式"""
        message = "some random commit"
        
        result = AIEngine.parse_commit_message(message)
        
        self.assertEqual(result["type"], "chore")
        self.assertEqual(result["subject"], "some random commit")
    
    def test_parse_commit_message_with_body(self):
        """测试带正文的提交信息"""
        message = """feat(api): implement new endpoint

This commit adds a new API endpoint for user management.
It includes authentication and validation."""
        
        result = AIEngine.parse_commit_message(message)
        
        self.assertEqual(result["type"], "feat")
        self.assertEqual(result["scope"], "api")
        self.assertEqual(result["subject"], "implement new endpoint")
        self.assertIn("adds a new API endpoint", result["body"])


if __name__ == "__main__":
    unittest.main()

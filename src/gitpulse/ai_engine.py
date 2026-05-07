"""
AI引擎 - 提供多后端AI支持，用于生成提交信息、PR描述等
支持OpenAI、Anthropic Claude、本地Ollama等后端
"""

import json
import re
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass
from enum import Enum
import urllib.request
import urllib.error


class AIProvider(Enum):
    """AI提供商枚举"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    OLLAMA = "ollama"
    OPENROUTER = "openrouter"


@dataclass
class AIConfig:
    """AI配置数据类"""
    provider: AIProvider
    api_key: str
    model: str
    base_url: Optional[str] = None
    temperature: float = 0.3
    max_tokens: int = 500


class AIEngine:
    """AI引擎 - 支持多后端"""
    
    # 默认模型配置
    DEFAULT_MODELS = {
        AIProvider.OPENAI: "gpt-4o-mini",
        AIProvider.ANTHROPIC: "claude-3-haiku-20240307",
        AIProvider.OLLAMA: "llama3.2",
        AIProvider.OPENROUTER: "openai/gpt-4o-mini",
    }
    
    # API端点
    API_ENDPOINTS = {
        AIProvider.OPENAI: "https://api.openai.com/v1/chat/completions",
        AIProvider.ANTHROPIC: "https://api.anthropic.com/v1/messages",
        AIProvider.OLLAMA: "http://localhost:11434/api/generate",
        AIProvider.OPENROUTER: "https://openrouter.ai/api/v1/chat/completions",
    }
    
    def __init__(self, config: AIConfig):
        self.config = config
        self._validate_config()
    
    def _validate_config(self):
        """验证配置"""
        if not self.config.api_key and self.config.provider != AIProvider.OLLAMA:
            raise ValueError(f"{self.config.provider.value} 需要提供API密钥")
        
        if not self.config.model:
            self.config.model = self.DEFAULT_MODELS.get(self.config.provider, "")
    
    def _make_request(self, url: str, headers: Dict, data: Dict) -> Dict:
        """发送HTTP请求"""
        request = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers=headers,
            method="POST"
        )
        
        try:
            with urllib.request.urlopen(request, timeout=60) as response:
                return json.loads(response.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            error_body = e.read().decode("utf-8")
            raise RuntimeError(f"API请求失败: {e.code} - {error_body}")
        except Exception as e:
            raise RuntimeError(f"请求异常: {str(e)}")
    
    def generate_commit_message(self, diff: str, context: Optional[Dict] = None) -> str:
        """生成提交信息"""
        # 截断diff以避免超出token限制
        max_diff_length = 4000
        truncated_diff = diff[:max_diff_length]
        if len(diff) > max_diff_length:
            truncated_diff += "\n... (diff已截断)"
        
        prompt = self._build_commit_prompt(truncated_diff, context)
        
        if self.config.provider == AIProvider.OPENAI:
            return self._call_openai(prompt)
        elif self.config.provider == AIProvider.ANTHROPIC:
            return self._call_anthropic(prompt)
        elif self.config.provider == AIProvider.OLLAMA:
            return self._call_ollama(prompt)
        elif self.config.provider == AIProvider.OPENROUTER:
            return self._call_openrouter(prompt)
        else:
            raise ValueError(f"不支持的AI提供商: {self.config.provider}")
    
    def _build_commit_prompt(self, diff: str, context: Optional[Dict]) -> str:
        """构建提交信息生成提示词"""
        base_prompt = """你是一个专业的Git提交信息生成助手。请根据以下代码变更生成符合Conventional Commits规范的提交信息。

要求：
1. 使用Conventional Commits格式: <type>(<scope>): <subject>
2. type可选: feat(新功能), fix(修复), docs(文档), style(格式), refactor(重构), perf(性能), test(测试), chore(构建)
3. subject使用祈使句，首字母小写，不超过50个字符
4. 如有必要，可添加body部分说明详细变更
5. 只输出提交信息，不要其他解释

代码变更：
```diff
{diff}
```
"""
        
        if context:
            context_str = json.dumps(context, indent=2, ensure_ascii=False)
            base_prompt += f"\n\n额外上下文:\n{context_str}"
        
        return base_prompt.format(diff=diff)
    
    def _call_openai(self, prompt: str) -> str:
        """调用OpenAI API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}"
        }
        
        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = self._make_request(
            self.config.base_url or self.API_ENDPOINTS[AIProvider.OPENAI],
            headers,
            data
        )
        
        return response["choices"][0]["message"]["content"].strip()
    
    def _call_anthropic(self, prompt: str) -> str:
        """调用Anthropic Claude API"""
        headers = {
            "Content-Type": "application/json",
            "x-api-key": self.config.api_key,
            "anthropic-version": "2023-06-01"
        }
        
        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature
        }
        
        response = self._make_request(
            self.config.base_url or self.API_ENDPOINTS[AIProvider.ANTHROPIC],
            headers,
            data
        )
        
        return response["content"][0]["text"].strip()
    
    def _call_ollama(self, prompt: str) -> str:
        """调用本地Ollama"""
        headers = {
            "Content-Type": "application/json"
        }
        
        data = {
            "model": self.config.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": self.config.temperature
            }
        }
        
        response = self._make_request(
            self.config.base_url or self.API_ENDPOINTS[AIProvider.OLLAMA],
            headers,
            data
        )
        
        return response["response"].strip()
    
    def _call_openrouter(self, prompt: str) -> str:
        """调用OpenRouter API"""
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.config.api_key}",
            "HTTP-Referer": "https://github.com/gitpulse",
            "X-Title": "GitPulse"
        }
        
        data = {
            "model": self.config.model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_tokens
        }
        
        response = self._make_request(
            self.config.base_url or self.API_ENDPOINTS[AIProvider.OPENROUTER],
            headers,
            data
        )
        
        return response["choices"][0]["message"]["content"].strip()
    
    def generate_pr_description(self, commits: List[str], diff_summary: str) -> str:
        """生成PR描述"""
        commits_text = "\n".join([f"- {c}" for c in commits[:10]])
        
        prompt = f"""请根据以下提交记录和变更摘要生成Pull Request描述。

要求：
1. 标题简洁明了，说明本次PR的主要目的
2. 描述包含变更内容、影响范围、测试说明
3. 使用Markdown格式
4. 如有破坏性变更请特别标注

最近提交:
{commits_text}

变更摘要:
{diff_summary}

请生成PR描述（包含标题和正文）:
"""
        
        if self.config.provider == AIProvider.OPENAI:
            return self._call_openai(prompt)
        elif self.config.provider == AIProvider.ANTHROPIC:
            return self._call_anthropic(prompt)
        elif self.config.provider == AIProvider.OLLAMA:
            return self._call_ollama(prompt)
        elif self.config.provider == AIProvider.OPENROUTER:
            return self._call_openrouter(prompt)
        else:
            raise ValueError(f"不支持的AI提供商: {self.config.provider}")
    
    def suggest_workflow(self, status: Dict, history: List[str]) -> List[str]:
        """基于当前状态建议工作流"""
        status_json = json.dumps(status, indent=2, ensure_ascii=False)
        history_text = "\n".join(history[-5:]) if history else "无历史记录"
        
        prompt = f"""作为Git工作流专家，请根据当前仓库状态提供操作建议。

当前状态:
{status_json}

最近操作历史:
{history_text}

请提供3-5条具体的Git操作建议，每条建议一行，格式为: [操作类型] 建议内容
例如:
[commit] 建议提交暂存区的变更
[branch] 建议创建新分支进行功能开发
"""
        
        if self.config.provider == AIProvider.OPENAI:
            response = self._call_openai(prompt)
        elif self.config.provider == AIProvider.ANTHROPIC:
            response = self._call_anthropic(prompt)
        elif self.config.provider == AIProvider.OLLAMA:
            response = self._call_ollama(prompt)
        elif self.config.provider == AIProvider.OPENROUTER:
            response = self._call_openrouter(prompt)
        else:
            raise ValueError(f"不支持的AI提供商: {self.config.provider}")
        
        # 解析建议
        suggestions = []
        for line in response.strip().split("\n"):
            line = line.strip()
            if line and (line.startswith("[") or "建议" in line):
                suggestions.append(line)
        
        return suggestions[:5]
    
    @staticmethod
    def parse_commit_message(message: str) -> Dict[str, str]:
        """解析提交信息"""
        lines = message.strip().split("\n")
        if not lines:
            return {"type": "chore", "scope": "", "subject": message, "body": ""}
        
        first_line = lines[0]
        
        # 解析Conventional Commit格式
        pattern = r"^(\w+)(?:\(([^)]+)\))?:\s*(.+)$"
        match = re.match(pattern, first_line)
        
        if match:
            return {
                "type": match.group(1),
                "scope": match.group(2) or "",
                "subject": match.group(3),
                "body": "\n".join(lines[1:]).strip()
            }
        else:
            return {
                "type": "chore",
                "scope": "",
                "subject": first_line,
                "body": "\n".join(lines[1:]).strip()
            }

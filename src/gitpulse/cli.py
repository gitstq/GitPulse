"""
GitPulse CLI - 命令行界面
"""

import sys
import os
import json
import argparse
from typing import Optional

from .core import GitPulse
from .ai_engine import AIProvider


# ANSI颜色代码
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_colored(text: str, color: str = ""):
    """打印彩色文本"""
    if color:
        print(f"{color}{text}{Colors.ENDC}")
    else:
        print(text)


def print_header(text: str):
    """打印标题"""
    print()
    print_colored("=" * 60, Colors.CYAN)
    print_colored(f"  {text}", Colors.BOLD + Colors.CYAN)
    print_colored("=" * 60, Colors.CYAN)
    print()


def print_success(text: str):
    """打印成功消息"""
    print_colored(f"✓ {text}", Colors.GREEN)


def print_warning(text: str):
    """打印警告消息"""
    print_colored(f"⚠ {text}", Colors.WARNING)


def print_error(text: str):
    """打印错误消息"""
    print_colored(f"✗ {text}", Colors.FAIL)


def print_info(text: str):
    """打印信息"""
    print_colored(f"ℹ {text}", Colors.BLUE)


def create_parser() -> argparse.ArgumentParser:
    """创建参数解析器"""
    parser = argparse.ArgumentParser(
        prog="gitpulse",
        description="GitPulse - AI驱动的Git工作流智能助手",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  gitpulse status              查看Git状态
  gitpulse suggest             获取提交建议
  gitpulse branch              获取分支建议
  gitpulse workflow            获取工作流建议
  gitpulse pr                  生成PR描述
  gitpulse config              查看配置
  gitpulse config --set-provider openai  设置AI提供商
        """
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--repo",
        default=".",
        help="Git仓库路径 (默认: 当前目录)"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # status命令
    status_parser = subparsers.add_parser(
        "status",
        aliases=["s"],
        help="查看Git状态概览"
    )
    
    # suggest命令
    suggest_parser = subparsers.add_parser(
        "suggest",
        aliases=["su"],
        help="获取提交信息建议"
    )
    suggest_parser.add_argument(
        "--no-ai",
        action="store_true",
        help="不使用AI，仅使用规则生成"
    )
    
    # branch命令
    branch_parser = subparsers.add_parser(
        "branch",
        aliases=["b"],
        help="获取分支名称建议"
    )
    
    # workflow命令
    workflow_parser = subparsers.add_parser(
        "workflow",
        aliases=["w"],
        help="获取工作流建议"
    )
    
    # pr命令
    pr_parser = subparsers.add_parser(
        "pr",
        help="生成PR描述"
    )
    pr_parser.add_argument(
        "--base",
        default="main",
        help="目标分支 (默认: main)"
    )
    
    # validate命令
    validate_parser = subparsers.add_parser(
        "validate",
        aliases=["v"],
        help="验证提交信息"
    )
    validate_parser.add_argument(
        "message",
        nargs="?",
        help="要验证的提交信息"
    )
    
    # config命令
    config_parser = subparsers.add_parser(
        "config",
        aliases=["c"],
        help="配置管理"
    )
    config_parser.add_argument(
        "--set-provider",
        choices=["openai", "anthropic", "ollama", "openrouter"],
        help="设置AI提供商"
    )
    config_parser.add_argument(
        "--set-model",
        help="设置AI模型"
    )
    config_parser.add_argument(
        "--set-temp",
        type=float,
        help="设置temperature (0.0-1.0)"
    )
    
    # setup命令
    setup_parser = subparsers.add_parser(
        "setup",
        help="初始化配置"
    )
    
    return parser


def cmd_status(gitpulse: GitPulse):
    """status命令"""
    print_header("📊 Git状态概览")
    
    try:
        status = gitpulse.status()
        
        print_colored(f"当前分支: {status['branch']}", Colors.BOLD)
        
        if status['ahead'] > 0:
            print_info(f"领先远程 {status['ahead']} 个提交")
        if status['behind'] > 0:
            print_warning(f"落后远程 {status['behind']} 个提交")
        
        print()
        
        if status['is_clean']:
            print_success("工作区干净，没有变更")
        else:
            if status['staged_count'] > 0:
                print_colored(f"\n📦 已暂存 ({status['staged_count']}):", Colors.GREEN)
                for f in status['staged_files'][:10]:
                    print(f"  + {f}")
                if len(status['staged_files']) > 10:
                    print(f"  ... 还有 {len(status['staged_files']) - 10} 个文件")
            
            if status['unstaged_count'] > 0:
                print_colored(f"\n📝 未暂存 ({status['unstaged_count']}):", Colors.WARNING)
                for f in status['unstaged_files'][:10]:
                    print(f"  ~ {f}")
                if len(status['unstaged_files']) > 10:
                    print(f"  ... 还有 {len(status['unstaged_files']) - 10} 个文件")
            
            if status['untracked_count'] > 0:
                print_colored(f"\n❓ 未跟踪 ({status['untracked_count']}):", Colors.BLUE)
                for f in status['untracked_files'][:10]:
                    print(f"  ? {f}")
                if len(status['untracked_files']) > 10:
                    print(f"  ... 还有 {len(status['untracked_files']) - 10} 个文件")
        
        print()
        
    except Exception as e:
        print_error(f"获取状态失败: {str(e)}")
        return 1
    
    return 0


def cmd_suggest(gitpulse: GitPulse, use_ai: bool = True):
    """suggest命令"""
    print_header("💡 提交信息建议")
    
    try:
        result = gitpulse.suggest_commit(use_ai=use_ai)
        
        if not result['success']:
            print_warning(result['message'])
            return 0
        
        # 显示变更统计
        summary = result['diff_summary']
        print_colored("变更统计:", Colors.BOLD)
        print(f"  文件: {summary['files_changed']}")
        print(f"  新增: {summary['insertions']} 行")
        print(f"  删除: {summary['deletions']} 行")
        print()
        
        # 显示建议
        print_colored("建议的提交信息:", Colors.BOLD)
        print()
        
        for i, suggestion in enumerate(result['suggestions'], 1):
            if suggestion['type'] == 'ai':
                print_colored(f"【AI生成】", Colors.CYAN)
            else:
                print_colored(f"【规则生成】", Colors.BLUE)
            
            print_colored(f"  {suggestion['message']}", Colors.BOLD + Colors.GREEN)
            
            if suggestion['parsed']:
                parsed = suggestion['parsed']
                print(f"  类型: {parsed.get('type', 'N/A')}")
                print(f"  范围: {parsed.get('scope', 'N/A')}")
                print(f"  主题: {parsed.get('subject', 'N/A')}")
            
            print()
        
        print_colored("使用建议:", Colors.BOLD)
        print("  git add .")
        print(f"  git commit -m \"<上述建议信息>\"")
        print()
        
    except Exception as e:
        print_error(f"生成建议失败: {str(e)}")
        return 1
    
    return 0


def cmd_branch(gitpulse: GitPulse):
    """branch命令"""
    print_header("🌿 分支名称建议")
    
    try:
        result = gitpulse.suggest_branch()
        
        print_colored("推荐的分支名称:", Colors.BOLD)
        print()
        for i, suggestion in enumerate(result['suggestions'], 1):
            print_colored(f"  {i}. {suggestion}", Colors.GREEN)
        
        print()
        print_colored("分支命名规范:", Colors.BOLD)
        for pattern, desc in result['naming_guide'].items():
            print(f"  {pattern:<20} - {desc}")
        
        print()
        print_colored("使用建议:", Colors.BOLD)
        print("  git checkout -b <分支名称>")
        print()
        
    except Exception as e:
        print_error(f"生成分支建议失败: {str(e)}")
        return 1
    
    return 0


def cmd_workflow(gitpulse: GitPulse):
    """workflow命令"""
    print_header("🔄 工作流建议")
    
    try:
        result = gitpulse.suggest_workflow()
        
        print_colored(f"推荐工作流: {result['workflow_name']}", Colors.BOLD + Colors.CYAN)
        print(f"{result['description']}")
        print()
        
        print_colored("执行检查清单:", Colors.BOLD)
        for item in result['checklist']:
            print(f"  {item}")
        
        if result['ai_suggestions']:
            print()
            print_colored("AI额外建议:", Colors.BOLD)
            for suggestion in result['ai_suggestions']:
                print(f"  • {suggestion}")
        
        print()
        
    except Exception as e:
        print_error(f"获取工作流建议失败: {str(e)}")
        return 1
    
    return 0


def cmd_pr(gitpulse: GitPulse, base_branch: str = "main"):
    """pr命令"""
    print_header("📝 PR描述生成")
    
    try:
        result = gitpulse.generate_pr(base_branch)
        
        print_colored("建议的PR标题:", Colors.BOLD)
        print_colored(f"  {result['title']}", Colors.GREEN)
        print()
        
        print_colored("PR描述:", Colors.BOLD)
        print("-" * 60)
        print(result['description'])
        print("-" * 60)
        print()
        
        print_colored("变更统计:", Colors.BOLD)
        print(f"  文件: {result['stats']['files_changed']}")
        print(f"  新增: {result['stats']['insertions']}")
        print(f"  删除: {result['stats']['deletions']}")
        print()
        
    except Exception as e:
        print_error(f"生成PR描述失败: {str(e)}")
        return 1
    
    return 0


def cmd_validate(gitpulse: GitPulse, message: Optional[str]):
    """validate命令"""
    print_header("✅ 提交信息验证")
    
    if not message:
        # 从参数或交互式输入
        message = input("请输入要验证的提交信息: ").strip()
    
    if not message:
        print_error("提交信息不能为空")
        return 1
    
    try:
        result = gitpulse.validate_commit(message)
        
        print_colored("验证结果:", Colors.BOLD)
        
        if result['valid'] and not result['warnings']:
            print_success("提交信息符合规范！")
        elif result['valid']:
            print_warning("提交信息有效，但有警告:")
            for warning in result['warnings']:
                print(f"  ⚠ {warning}")
        else:
            print_error("提交信息不符合规范:")
            for error in result['errors']:
                print(f"  ✗ {error}")
        
        if result['suggestions']:
            print()
            print_colored("改进建议:", Colors.BOLD)
            for suggestion in result['suggestions']:
                print(f"  💡 {suggestion}")
        
        print()
        print_colored("提交类型参考:", Colors.BOLD)
        for type_key, type_desc in result['convention_guide'].items():
            print(f"  {type_key:<10} {type_desc}")
        
        print()
        
    except Exception as e:
        print_error(f"验证失败: {str(e)}")
        return 1
    
    return 0


def cmd_config(gitpulse: GitPulse, args):
    """config命令"""
    print_header("⚙️ 配置管理")
    
    try:
        if args.set_provider:
            result = gitpulse.config("ai_provider", args.set_provider)
            print_success(result['message'])
            print_info("请设置对应的环境变量:")
            env_vars = {
                "openai": "OPENAI_API_KEY",
                "anthropic": "ANTHROPIC_API_KEY",
                "openrouter": "OPENROUTER_API_KEY",
                "ollama": "无需API密钥"
            }
            print(f"  export {env_vars.get(args.set_provider, 'API_KEY')}=your_key_here")
        
        elif args.set_model:
            result = gitpulse.config("model", args.set_model)
            print_success(result['message'])
        
        elif args.set_temp is not None:
            result = gitpulse.config("temperature", str(args.set_temp))
            print_success(result['message'])
        
        else:
            # 显示配置
            result = gitpulse.config()
            print_colored("当前配置:", Colors.BOLD)
            print(f"  配置文件: {result['config_path']}")
            print()
            for key, value in result['config'].items():
                print(f"  {key:<20} = {value}")
        
        print()
        
    except Exception as e:
        print_error(f"配置操作失败: {str(e)}")
        return 1
    
    return 0


def cmd_setup(gitpulse: GitPulse):
    """setup命令"""
    print_header("🚀 GitPulse 初始化")
    
    print_colored("欢迎使用GitPulse！", Colors.BOLD + Colors.CYAN)
    print()
    print("GitPulse是一个AI驱动的Git工作流智能助手，可以帮助你:")
    print("  • 生成符合规范的提交信息")
    print("  • 推荐合适的分支名称")
    print("  • 提供工作流建议")
    print("  • 生成PR描述")
    print()
    
    print_colored("配置AI提供商:", Colors.BOLD)
    print("  1. OpenAI (推荐)")
    print("  2. Anthropic Claude")
    print("  3. OpenRouter (免费选项)")
    print("  4. Ollama (本地模型)")
    print()
    
    choice = input("请选择 (1-4): ").strip()
    
    providers = {
        "1": ("openai", "OPENAI_API_KEY"),
        "2": ("anthropic", "ANTHROPIC_API_KEY"),
        "3": ("openrouter", "OPENROUTER_API_KEY"),
        "4": ("ollama", None)
    }
    
    if choice in providers:
        provider, env_key = providers[choice]
        gitpulse.config("ai_provider", provider)
        print_success(f"已设置AI提供商: {provider}")
        
        if env_key:
            print()
            print_colored("环境变量设置:", Colors.BOLD)
            print(f"  export {env_key}=your_api_key_here")
            print()
            print_warning("请将上述命令添加到您的shell配置文件中(.bashrc/.zshrc)")
    else:
        print_warning("跳过AI配置，您可以稍后使用 'gitpulse config' 命令设置")
    
    print()
    print_success("初始化完成！")
    print()
    print_colored("快速开始:", Colors.BOLD)
    print("  gitpulse status    - 查看Git状态")
    print("  gitpulse suggest   - 获取提交建议")
    print("  gitpulse --help    - 查看所有命令")
    print()
    
    return 0


def main():
    """主入口"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 0
    
    # 初始化GitPulse
    try:
        gitpulse = GitPulse(repo_path=args.repo)
    except ValueError as e:
        print_error(str(e))
        return 1
    except Exception as e:
        print_error(f"初始化失败: {str(e)}")
        return 1
    
    # 执行命令
    if args.command in ["status", "s"]:
        return cmd_status(gitpulse)
    
    elif args.command in ["suggest", "su"]:
        return cmd_suggest(gitpulse, use_ai=not args.no_ai)
    
    elif args.command in ["branch", "b"]:
        return cmd_branch(gitpulse)
    
    elif args.command in ["workflow", "w"]:
        return cmd_workflow(gitpulse)
    
    elif args.command == "pr":
        return cmd_pr(gitpulse, args.base)
    
    elif args.command in ["validate", "v"]:
        return cmd_validate(gitpulse, args.message)
    
    elif args.command in ["config", "c"]:
        return cmd_config(gitpulse, args)
    
    elif args.command == "setup":
        return cmd_setup(gitpulse)
    
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())

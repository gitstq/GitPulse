.PHONY: help install install-dev test lint format clean build publish

help:
	@echo "GitPulse Makefile"
	@echo ""
	@echo "可用命令:"
	@echo "  install      - 安装包"
	@echo "  install-dev  - 安装开发依赖"
	@echo "  test         - 运行测试"
	@echo "  lint         - 运行代码检查"
	@echo "  format       - 格式化代码"
	@echo "  clean        - 清理构建文件"
	@echo "  build        - 构建分发包"
	@echo "  publish      - 发布到PyPI"

install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pip install -r requirements.txt

test:
	pytest tests/ -v --cov=gitpulse --cov-report=html

lint:
	flake8 src/gitpulse
	mypy src/gitpulse

format:
	black src/gitpulse

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python setup.py sdist bdist_wheel

publish: build
	twine check dist/*
	twine upload dist/*

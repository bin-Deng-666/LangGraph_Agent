# Agent Project

一个用于构建和运行智能代理（Agent）的项目框架。

## 项目概述

本项目提供了一个灵活的Agent开发框架，允许开发者在`examples`目录中构建各种类型的智能代理。每个Agent都可以独立运行，专注于解决特定领域的问题。

## 项目结构

```
Agent/
├── examples/          # 示例Agent目录
│   ├── simple_agent/  # 简单时间查询Agent
│   └── general_assistant/ # 通用助手Agent
├── src/               # 核心源代码
├── resources/         # 资源文件
├── config.py          # 配置文件
├── requirements.txt   # 依赖包
└── README.md          # 项目说明
```

## 使用方法

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 运行示例Agent
进入具体的Agent目录运行相应的demo：
```bash
cd examples/simple_agent
python simple_agent.py
```

### 3. 创建新的Agent
在`examples`目录下创建新的Agent文件夹，参考现有示例实现您的Agent逻辑。

### 4. 配置环境
创建并配置环境变量文件：
```bash
# 编辑.env文件设置您的API密钥配置

# 初始化环境变量（Linux/Mac）
source .env
# 或者使用dotenv自动加载（推荐，无需手动source）
python -c "from config import *; print('环境变量加载成功')"
```

## 开发指南

1. **Agent设计**: 每个Agent应该专注于单一职责
2. **模块化**: 保持代码的模块化和可复用性
3. **文档**: 为每个Agent提供清晰的文档说明
4. **测试**: 为重要功能编写测试用例
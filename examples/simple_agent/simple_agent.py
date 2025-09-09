"""
极简React Agent示例
展示React Agent的基本初始化流程及关键功能调用
"""

import sys
import os
import uuid
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../..'))

from langgraph.prebuilt import create_react_agent
from langgraph.graph.state import CompiledStateGraph
from src.models import get_model
from src.tools import get_current_datetime, execute_command
from src.prompts import apply_prompt_template


simple_agent = create_react_agent(
    model=get_model(),
    tools=[get_current_datetime, execute_command],
    prompt=apply_prompt_template("simple_react", subject="simple_agent")
)

def run_agent(agent:CompiledStateGraph, messages:list):
    result = agent.stream(
        {"messages": messages},
        stream_mode="values",
        config={"thread_id": thread_id},
    )
    for chunk in result:
        message = chunk["messages"]
        last_message = message[-1]
        last_message.pretty_print()
    return message

# 3. 主程序入口
if __name__ == "__main__":
    # 使用固定的thread_id来保持对话状态
    thread_id = uuid.uuid4()
    messages = []
    
    while True:
        query = input("输入你的问题:")
        if query.strip().lower() == 'q':
            break
            
        # 添加用户消息到对话历史
        messages.append({"role": "user", "content": query})
        
        # 运行agent并获取完整的对话历史
        messages = run_agent(simple_agent, messages)
        
        # 只保留最近的10轮对话以避免token过长
        if len(messages) > 20:
            messages = messages[-20:]
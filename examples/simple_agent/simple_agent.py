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
from src.tools import get_current_datetime
from src.prompts import apply_prompt_template


simple_agent = create_react_agent(
    model=get_model(),
    tools=[get_current_datetime],
    prompt=apply_prompt_template("simple_react", subject="simple_agent")
)

def run_agent(agent:CompiledStateGraph, message:str):
    result = agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode="values",
        config={"thread_id": uuid.uuid4()},
    )
    for chunk in result:
        message = chunk["messages"]
        last_message = message[-1]
        last_message.pretty_print()

# 3. 主程序入口
if __name__ == "__main__":
    while True:
        query = input("输入你的问题:")
        if query.strip().lower() == 'q':
            break
        run_agent(simple_agent, message=query)
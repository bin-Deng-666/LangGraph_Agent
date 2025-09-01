import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import uuid
from langchain.tools import tool
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt import create_react_agent
from langgraph_supervisor import create_supervisor

from src.models import get_model
from src.prompts import apply_prompt_template
from src.tools import get_current_date, get_metric_definition, get_table_metadata, sql_execute, get_all_metric_names

# 1. 定义问题改写Agent
# 职责：识别并补充用户问题中的日期信息。
query_rewriter_agent = create_react_agent(
    get_model(),
    tools=[get_current_date, get_all_metric_names],
    name="query_rewriter_agent",
    prompt=apply_prompt_template(template="query_rewriter", subject="db_assistant"),
)

# 2. 定义故障排查Agent
# 职责：分析用户问题，将自然语言转换为SQL并执行，查询表的结构信息、指标定义或分析错误。
# 提示词应引导其理解表的血缘关系。
troubleshooting_agent = create_react_agent(
    get_model(),
    tools=[get_metric_definition, get_table_metadata, sql_execute],
    name="troubleshooting_agent",
    prompt=apply_prompt_template(template="troubleshooting", subject="db_assistant"),
)

# 3. 定义总结Agent
# 职责：整合其他Agent的结果，形成最终的、易于理解的报告。
summary_agent = create_react_agent(
    get_model(),
    tools=[],
    name="summary_agent",
    prompt=apply_prompt_template(template="summary", subject="db_assistant"),
)

# 4. 创建总Agent (Supervisor)
# 职责：作为总指挥，根据用户问题协调其他Agent完成任务。
supervisor = create_supervisor(
    agents=[query_rewriter_agent, troubleshooting_agent, summary_agent],
    model=get_model(),
    prompt=apply_prompt_template(template="supervisor", subject="db_assistant"),
).compile()

def run_agent(agent:CompiledStateGraph,message:str):
    result = agent.stream(
        {"messages": [{"role": "user", "content": message}]},
        stream_mode="values",
        config={"thread_id": uuid.uuid4()},
    )
    for chunk in result:
        message = chunk["messages"]
        last_message = message[-1]
        last_message.pretty_print()

if __name__ == '__main__':
    while True:
        query = input("输入你的问题:")
        if query.strip().lower() == 'q':
            break
        run_agent(supervisor, message=query)
        # 也可以生成流程图
        # supervisor.get_graph().draw_mermaid_png(output_file_path="db_mas_agent.png")
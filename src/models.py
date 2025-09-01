import os
from langchain_openai import ChatOpenAI
from config import SILICONFLOW_API_KEY

# 通用模型调用函数
def get_model(model_name: str = "deepseek-ai/DeepSeek-V3.1", temperature: float = 0) -> ChatOpenAI:
    """
    获取配置好的模型实例
    
    Args:
        model_name: 模型名称
        temperature: 生成温度，0-1之间，值越高越随机
        
    Returns:
        ChatOpenAI: 配置好的模型实例
    """
    # 统一使用SiliconFlow API，通过model_name参数切换不同模型
    return ChatOpenAI(
        model=model_name,
        base_url="https://api.siliconflow.cn/v1",
        api_key=SILICONFLOW_API_KEY,
        temperature=temperature,
    )

# 保留原有的siliconflow实例用于向后兼容
siliconflow = get_model("deepseek-ai/DeepSeek-V3.1", temperature=0)
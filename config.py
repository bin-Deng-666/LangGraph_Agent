import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# API密钥配置 - 从环境变量读取，如果不存在则使用默认值
SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "your_siliconflow_api_key_here")

# 资源目录配置
resource_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")

# 确保资源目录存在
os.makedirs(resource_dir, exist_ok=True)

# 提示词模板目录配置
template_dir = os.path.join(resource_dir, "prompts")
os.makedirs(template_dir, exist_ok=True)
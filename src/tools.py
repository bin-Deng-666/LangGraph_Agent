from langchain.tools import tool
from datetime import datetime

@tool
def get_current_date() -> str:
    """获取当前日期，格式为YYYY-MM-DD"""
    return datetime.now().strftime("%Y-%m-%d")

@tool
def get_current_datetime() -> str:
    """获取当前精确时间点，格式为YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
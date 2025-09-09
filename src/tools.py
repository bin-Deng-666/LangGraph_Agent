from langchain.tools import tool
from datetime import datetime
import requests
import os
import subprocess
from typing import Dict, List

@tool
def get_current_datetime() -> str:
    """获取当前精确时间点，格式为YYYY-MM-DD HH:MM:SS"""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


@tool
def execute_command(command: str) -> Dict[str, str]:
    """
    执行命令行命令并返回结果
    
    Args:
        command: 要执行的命令行命令
        
    Returns:
        包含命令执行结果或错误的字典
    """
    try:
        # 安全地执行命令，设置超时时间为30秒
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.getcwd()  # 在当前工作目录执行
        )
        
        if result.returncode == 0:
            return {
                "success": True,
                "output": result.stdout,
                "command": command
            }
        else:
            return {
                "success": False,
                "error": result.stderr,
                "output": result.stdout,
                "returncode": result.returncode,
                "command": command
            }
            
    except subprocess.TimeoutExpired:
        return {"error": "命令执行超时（30秒）", "command": command}
    except Exception as e:
        return {"error": f"命令执行失败: {str(e)}", "command": command}
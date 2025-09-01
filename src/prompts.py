import os
from jinja2 import Environment, FileSystemLoader
from config import resource_dir

def apply_prompt_template(template: str, subject="", **kwargs) -> str:
    """
    应用提示词模板
    
    Args:
        template: 模板名称
        subject: 主题目录
        **kwargs: 模板参数
    
    Returns:
        str: 渲染后的提示词
    """
    template_dir = os.path.join(resource_dir, "{}".format(subject), "prompts")
    loader = FileSystemLoader(template_dir)
    env = Environment(loader=loader)
    template = env.get_template(f"{template}.jinja-md")
    return template.render(**kwargs)

# 示例使用
if __name__ == "__main__":
    print(apply_prompt_template("db_react"))
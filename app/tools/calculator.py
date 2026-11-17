"""计算工具。"""
from langchain_core.tools import tool


@tool
def calculator(expression: str) -> float:
    """执行数学计算。参数 expression 是数学表达式，例如 '3500*12'、'(3+5)*2'。
    注意：表达式中请使用数字和运算符，不要包含中文单位（如"万"）。"""
    # 此处用 eval 求值；生产环境建议改用 ast 安全解析（如 asteval）
    return eval(expression, {"__builtins__": {}}, {})

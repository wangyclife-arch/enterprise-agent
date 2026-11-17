"""Agent 状态定义：messages 使用 add_messages 归约器实现追加语义。"""
from typing import Annotated, TypedDict

from langgraph.graph.message import add_messages


class AgentState(TypedDict):
    """智能体共享状态"""
    messages: Annotated[list, add_messages]   # 对话历史（自动追加合并）

"""员工手册检索工具：复用 RAG 检索能力。"""
from langchain_core.tools import tool

from app.services import rag_service


@tool
def search_employee_handbook(question: str) -> str:
    """查询公司员工手册，回答考勤、请假、薪资、福利、晋升等公司制度问题。
    参数 question 是具体的制度问题，例如"年假最长多少天"。"""
    results = rag_service.search(question, k=3)
    return "\n\n".join(results)

"""意图识别：用 with_structured_output 判断问题是否需要检索知识库。"""
from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

from app.core.llm import get_llm


class QuestionIntent(BaseModel):
    """问题的结构化分类结果"""

    category: Literal["company_policy", "chat", "calculation", "weather", "other"] = Field(
        description="问题类别：company_policy=公司制度咨询；chat=闲聊；calculation=数学计算；weather=天气；other=其他"
    )
    needs_knowledge_base: bool = Field(
        description="是否需要查询公司知识库才能回答：制度类问题为 true；闲聊/通用知识为 false"
    )
    summary: str = Field(description="用一句话概括用户想问什么")


_INTENT_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", "你是问题分类器。请把用户问题分类，并判断是否需要查询公司知识库。"),
        ("human", "问题：{question}"),
    ]
)


def classify_question(question: str) -> QuestionIntent:
    """对问题做结构化分类（强制按 QuestionIntent 格式输出）"""
    chain = _INTENT_PROMPT | get_llm(temperature=0).with_structured_output(
        QuestionIntent, method="function_calling"
    )
    return chain.invoke({"question": question})

"""聊天接口：RAG 问答、SSE 流式问答、Agent 执行与审批恢复。"""
from fastapi import APIRouter, Depends

from fastapi.responses import StreamingResponse
from sse_starlette.sse import EventSourceResponse

from app.auth import require_admin
from app.core.llm import get_llm
from app.models import User
#接口的约定，接收啥样的格式，返还啥样的格式
from app.schemas.chat import (
    AgentRequest,
    AgentResponse,
    ApproveRequest,
    ChatRequest,
    ChatResponse,
)
from app.services import agent_service, rag_service  #后厨真正干活的地方

router = APIRouter(prefix="/chat", tags=["聊天"])


@router.post("", response_model=ChatResponse) #声明接口（窗口）的地址，相当于挂牌子让人知道这个接口在哪
def chat(req: ChatRequest):  #接口本身相当于柜台服务员，用来接单，传单，再按约定格式返回
    """普通问答（路由版 RAG + 多轮记忆：先判断要不要查库，闲聊直接回答，制度问题走检索+Rerank）"""
    reply = rag_service.routed_answer(req.message, req.session_id)
    return ChatResponse(reply=reply, session_id=req.session_id)


@router.post("/stream")
async def chat_stream(req: ChatRequest):
    """流式问答（SSE 打字机效果）"""

    async def event_generator():
        yield {"event": "start", "data": "begin"}
        async for chunk in get_llm(temperature=0.2).astream(req.message):
            yield {"event": "message", "data": chunk.content}
        yield {"event": "end", "data": "done"}

    return EventSourceResponse(event_generator())


@router.post("/agent", response_model=AgentResponse)
def agent(req: AgentRequest):
    """智能体问答：自主决定调工具；敏感操作会停下来等审批"""
    result = agent_service.run(req.message, req.session_id)
    return AgentResponse(**result)


@router.post("/agent/approve", response_model=AgentResponse)
def agent_approve(req: ApproveRequest, admin: User = Depends(require_admin)):
    """人工审批（需管理员登录）：同意/拒绝智能体的敏感操作"""
    result = agent_service.approve(req.thread_id, req.approve, decided_by=admin.username)
    return AgentResponse(**result)

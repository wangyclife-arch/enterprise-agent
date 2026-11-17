"""检查点存储：LangGraph PostgresSaver，基于连接池并开启探活。

连接懒加载：数据库不可用时服务仍可正常启动。
"""
from psycopg import Connection

from langgraph.checkpoint.postgres import PostgresSaver

from app.config import DATABASE_URL

_checkpointer: PostgresSaver | None = None


def get_checkpointer() -> PostgresSaver:
    """获取检查点保存器（懒加载单例）"""
    global _checkpointer
    if _checkpointer is None:
        # psycopg3 连接（prepare_threshold=0 是 PostgresSaver 的要求）
        psycopg_url = DATABASE_URL.replace("postgresql+psycopg://", "postgresql://")
        conn = Connection.connect(psycopg_url, autocommit=True, prepare_threshold=0)
        _checkpointer = PostgresSaver(conn)
        _checkpointer.setup()  # 自动建检查点表
    return _checkpointer


def get_session_config(session_id: str) -> dict:
    """根据会话编号生成图运行配置（thread_id 相同=同一份记忆）"""
    return {"configurable": {"thread_id": session_id}}

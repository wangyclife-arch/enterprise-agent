"""重排序：调用 Rerank API 对粗筛结果精排，不可用时返回原顺序。"""
import json
import urllib.request

from app.config import EMBEDDING_API_KEY, RERANK_BASE_URL, RERANK_MODEL, USE_RERANK


def rerank(query: str, documents: list[str], top_n: int = 3) -> list[dict]:
    """调用 rerank 接口，返回分数最高的 top_n 条。
    返回：[{"index": 0, "relevance_score": 0.9}, ...]（已按分数降序）"""
    body = json.dumps(
        {
            "model": RERANK_MODEL,
            "query": query,
            "documents": documents,
            "top_n": top_n,
        }
    ).encode("utf-8")
    req = urllib.request.Request(
        RERANK_BASE_URL,
        data=body,
        headers={
            "Authorization": f"Bearer {EMBEDDING_API_KEY}",
            "Content-Type": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))
    return data.get("results", [])

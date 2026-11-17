"""数据库：SQLAlchemy 引擎与会话工厂、建表、pgvector 扩展初始化。"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# 引擎：惰性连接（真正用到才连数据库）
engine = create_engine(DATABASE_URL, pool_pre_ping=True)

# 会话工厂：每次操作数据库时创建一个 Session
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)

# 数据表的地基：app/models.py 里所有表都继承它
Base = declarative_base()


def get_db():
    """FastAPI 依赖：每个请求一个数据库会话，用完自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """启动时：先启用 pgvector 扩展，再创建所有表（幂等：已存在就不重复建）"""
    # （pgvector/pgvector 镜像里已安装，但要在每个数据库里激活）
    with engine.connect() as conn:
        conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        conn.commit()

    from app import models  # noqa: F401  确保模型已注册

    Base.metadata.create_all(bind=engine)

    # 简易"迁移"：老库 users 表没有 avatar 列 → 补上（项目没上迁移工具，用 ALTER 兜底）
    with engine.begin() as conn:
        conn.execute(
            text("ALTER TABLE users ADD COLUMN IF NOT EXISTS avatar VARCHAR(255) DEFAULT '👤'")
        )
        # 老库 avatar 是 VARCHAR(20)，图片路径较长 → 扩容
        conn.execute(text("ALTER TABLE users ALTER COLUMN avatar TYPE VARCHAR(255)"))

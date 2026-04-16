from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# For demo: using SQLite async for easy startup, but user asked for PostgreSQL.
# Will use PostgreSQL env var if provided, else fallback to sqlite for dev.

DATABASE_URL = "postgresql+asyncpg://admin:admini@localhost:5432/learn_claude"

engine = create_async_engine(DATABASE_URL, echo=False)
async_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with async_session() as session:
        yield session

import os
from typing import AsyncGenerator
import uuid
from sqlalchemy import String, Boolean, ForeignKey, Column
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, declared_attr, relationship
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.dialects.sqlite import JSON

DATABASE_URL = "sqlite+aiosqlite:///./data/mediagent.db"
os.makedirs("./data", exist_ok=True)

class Base(DeclarativeBase):
    pass

class User(SQLAlchemyBaseUserTableUUID, Base):
    pass

# We will let fastapi-users configure standard columns like email, hashed_password, is_active

class ClinicalNoteRecord(Base):
    __tablename__ = "clinical_notes"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(ForeignKey("user.id"), nullable=False)
    raw_note = Column(String, nullable=False)
    extracted_codes = Column(JSON, nullable=True) # JSON list
    guardrail_flags = Column(JSON, nullable=True)
    prior_auth_status = Column(String, nullable=True)
    overall_status = Column(String, nullable=True)
    audit_trail = Column(JSON, nullable=True)

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

from fastapi import Depends

async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)

import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Float, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase

load_dotenv()
DB_DIR = os.path.abspath(os.getenv('DB_DIR'))
engine = create_async_engine(f"sqlite+aiosqlite:///{DB_DIR}/database.db")
meta = MetaData()
Session = async_sessionmaker(bind=engine)
session = Session()


async def async_database() -> AsyncSession:
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)
    return session


class Base(AsyncAttrs, DeclarativeBase):
    pass


class Money(Base):
    __tablename__ = "money"
    index = Column('index', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer)
    coins = Column('coins', Integer)
    guild = Column('guild', Integer)


class Tasks(Base):
    __tablename__ = "tasks"
    task = Column('task', Integer, primary_key=True)
    year = Column('year', Integer)
    is_active = Column('is_active', Integer)
    collab = Column('collab', Integer)
    multiple_tracks = Column('multiple_tracks', Integer)
    speed_tasks = Column('speed_task', Integer)


class Submissions(Base):
    __tablename__ = "submissions"
    user_id = Column('id', Integer, primary_key=True)
    task = Column('task', Integer)
    name = Column('name', String)
    url = Column('url', String)
    time = Column('time', Float)
    dq = Column('dq', Integer)
    dq_reason = Column('dq_reason', String)


class Userbase(Base):
    __tablename__ = "userbase"
    index = Column('index', Integer, primary_key=True, autoincrement=True)
    user_id = Column('user_id', Integer)
    user = Column('user', String)
    display_name = Column('display_name', String)


class SubmissionChannel(Base):
    __tablename__ = "submission_channel"
    index = Column(Integer, primary_key=True)
    comp = Column('comp', String)
    channel_id = Column('channel_id', Integer)
    guild_id = Column('guild_id', Integer)


class LogChannel(Base):
    __tablename__ = "log_channel"
    index = Column('index', Integer, primary_key=True)
    channel_id = Column('channel_id', Integer)
    comp = Column('comp', String)
    guild_id = Column('guild_id', Integer)


class HostRole(Base):
    __tablename__ = "host_role"
    index = Column(Integer, primary_key=True)
    role_id = Column('role_id', Integer)
    name = Column('name', String)
    comp = Column('comp', String)
    guild_id = Column('guild_id', Integer)

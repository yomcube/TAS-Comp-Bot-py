import os
from dotenv import load_dotenv
from sqlalchemy import Column, Integer, String, Float, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession, AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, declarative_base


class Base(AsyncAttrs, DeclarativeBase):
    pass


load_dotenv()
DB_DIR = os.path.abspath(os.getenv('DB_DIR'))
engine = create_async_engine(f"sqlite+aiosqlite:///{DB_DIR}/database.db")
meta = MetaData()
Session = async_sessionmaker(bind=engine, autocommit=False, future=True, expire_on_commit=False, class_=AsyncSession)


def get_session():
    return async_sessionmaker(bind=engine, autocommit=False, future=True, expire_on_commit=False, class_=AsyncSession)()


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
    team_size = Column('team_size', Integer)
    multiple_tracks = Column('multiple_tracks', Integer)
    speed_task = Column('speed_task', Integer)


class Submissions(Base):
    __tablename__ = "submissions"
    user_id = Column('user_id', Integer, primary_key=True)
    task = Column('task', Integer)
    name = Column('name', String)
    url = Column('url', String)
    time = Column('time', Float)
    dq = Column('dq', Integer)
    dq_reason = Column('dq_reason', String)
    character = Column('character', String)
    vehicle = Column('vehicle', String)

class SpeedTask(Base):
    __tablename__ = "speedtask"
    user_id = Column('user_id', Integer, primary_key=True)
    end_time = Column('end_time', Integer)
    active = Column('active', String)


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


class Teams(Base):
    __tablename__ = "teams"
    index = Column('index', Integer, primary_key=True, autoincrement=True)
    team_name = Column('team_name', String)
    leader = Column('leader', Integer, nullable=False)
    user2 = Column('user2', Integer, nullable=True)
    user3 = Column('user3', Integer, nullable=True)
    user4 = Column('user4', Integer, nullable=True)


class LogChannel(Base):
    __tablename__ = "log_channel"
    index = Column('index', Integer, primary_key=True)
    channel_id = Column('channel_id', Integer)
    comp = Column('comp', String)
    guild_id = Column('guild_id', Integer)
    
class JoinChannel(Base):
    __tablename__ = "join_channel"
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
    
class SeekingChannel(Base):
    __tablename__ = "seeking_channel"
    index = Column(Integer, primary_key=True)
    comp = Column('comp', String)
    channel_id = Column('channel_id', Integer)
    guild_id = Column('guild_id', Integer)

class SpeedTaskTime(Base):
    __tablename__ = "speedtasktime"
    index = Column(Integer, primary_key=True)
    comp = Column('comp', String)
    time = Column('time', Float, default = 4.0)
    guild_id = Column('guild_id', Integer)

class SpeedTaskDesc(Base):
    __tablename__ = "speedtaskdesc"
    index = Column(Integer, primary_key=True)
    comp = Column('comp', String)
    desc = Column('desc', Integer)
    guild_id = Column('guild_id', Integer)


async def db_connect():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

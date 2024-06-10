import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, Column, Integer, String, QueuePool, Float
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

load_dotenv()
DB_DIR = os.getenv('DB_DIR')
Base = declarative_base()

engine_pool = create_engine(f"sqlite://{DB_DIR.partition('.')[-1]}/database.db")
Base.metadata.create_all(engine_pool)
Session = sessionmaker(bind=engine_pool)
session = Session()


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
    guild_id = Column('guild_id', Integer)
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
    guild_id = Column('guild_id', Integer)


class HostRole(Base):
    __tablename__ = "host_role"
    index = Column(Integer, primary_key=True)
    role_id = Column('role_id', Integer)
    name = Column('name', String)
    comp = Column('comp', String)
    guild_id = Column('guild_id', Integer)

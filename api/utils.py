import hashlib
import os
import aiohttp
import discord
from urllib.parse import urlparse
from discord.ext import commands
from sqlalchemy import select, insert, update, inspect, or_
from api.db_classes import Money, Tasks, Teams, HostRole, SubmitterRole, get_session, TasksChannel, AnnouncementsChannel
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
DB_DIR = os.getenv('DB_DIR')


async def get_balance(user_id, guild):
    async with get_session() as session:
        money = (await session.scalars(select(Money.coins).where(Money.user_id == user_id))).first()
        if money is None:
            balance = 500
            stmt = (insert(Money).values(guild=guild, user_id=user_id, coins=balance))
            await session.execute(stmt)
            await session.commit()

        else:
            balance = money
        return balance


async def update_balance(user_id, guild, new_balance):
    async with get_session() as session:
        stmt = (update(Money).values(guild=guild, user_id=user_id, coins=new_balance).where(Money.user_id == user_id))
        await session.execute(stmt)
        await session.commit()


async def add_balance(user_id, server_id, amount):
    current_balance = await get_balance(user_id, server_id)
    new_balance = current_balance + amount
    await update_balance(user_id, server_id, new_balance)


async def deduct_balance(user_id, guild, amount):
    current_balance = await get_balance(user_id, guild)
    new_balance = max(current_balance - amount, 0)  # Ensure balance doesn't go negative
    await update_balance(user_id, guild, new_balance)


async def get_host_role(guild_id):
    default = DEFAULT
    # Retrieves the host role. By default, on the server, the default host role is 'Host'.
    async with get_session() as session:
        host_role = (await session.scalars(select(HostRole.role_id).where(HostRole.comp == default and HostRole.guild_id == guild_id))).first()

        if host_role:
            return host_role
        else:
            return None
        
        
async def get_submitter_role(guild_id):
    default = DEFAULT
    # Retrieves the submitter role. By default, on the server, the default submitter role is 'submitter'.
    async with get_session() as session:
        submitter_role = (await session.scalars(select(SubmitterRole.role_id).where(SubmitterRole.comp == default and SubmitterRole.guild_id == guild_id))).first()

        if submitter_role:
            return submitter_role
        else:
            return None


async def get_tasks_channel(comp):
    async with get_session() as session:
        query = select(TasksChannel.channel_id).where(TasksChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No tasks channel found for '{comp}'.")
            return None
        return channel[0]

async def get_announcement_channel(comp):
    async with get_session() as session:
        query = select(AnnouncementsChannel.channel_id).where(AnnouncementsChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No announcements channel found for '{comp}'.")
            return None
        return channel[0]


def has_host_role():
    async def predicate(ctx):
        role = await get_host_role(ctx.message.guild.id)
        # Check if the role is a name
        has_role = discord.utils.get(ctx.author.roles, id=role) is not None
        return has_role

    return commands.check(predicate)


async def download_from_url(url) -> str:
    try:
        url_parsed = urlparse(url)
        filename, file_extension = os.path.splitext(os.path.basename(url_parsed.path))
        file_path = os.path.join(DOWNLOAD_DIR, f"{filename}{file_extension}")

        async with aiohttp.get(url) as file:
            if not file.ok:
                return None
            open(file_path, 'wb').write(file.content)

            return file_path

    except:

        return None


def readable_to_float(time_str):
    """Convert a time string 'M:SS.mmm' to seconds (float)."""
    try:
        minutes, seconds = time_str.split(':')
        minutes = int(minutes)
        seconds = float(seconds)
        total_seconds = minutes * 60 + seconds
        return total_seconds
    except ValueError:
        print("Invalid time format. Expected 'MM:SS.mmm'.")


def float_to_readable(seconds):
    """Convert seconds (float) to a time string 'M:SS.mmm'."""

    seconds = float(seconds)

    if seconds < 0:
        print("Seconds cannot be negative.")
        return

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    time_str = f"{minutes}:{remaining_seconds:06.3f}"
    return time_str


async def is_task_currently_running():
    """Check if a task is currently running. Returns a list with the parameters of active task, if so."""
    # Is a task running?
    # Does this need to be a function even?
    async with get_session() as session:
        active = (await session.execute(select(Tasks.task, Tasks.year, Tasks.is_active, Tasks.team_size,
                                               Tasks.speed_task, Tasks.multiple_tracks, Tasks.deadline, Tasks.is_released)
                                        .where(Tasks.is_active == 1))).first()
        return active


async def get_team_size():
    """Retrieves the team size of the running task. Over 1 means it is a collab task"""
    current_task = await is_task_currently_running()
    if current_task is not None:
        return current_task[3]
    else:
        return None

async def is_in_team(id):
    """Returns if a certain id is in a team (found in the Teams db)"""
    async with get_session() as session:
        inspector = inspect(Teams)
        columns = inspector.columns
        conditions = [getattr(Teams, column.name) == id for column in columns if
                      column.type.python_type == int]
        stmt = select(Teams).filter(or_(*conditions))
        result = await session.execute(stmt)
        results = result.scalars().all()
        return results

async def get_leader(id):
    """Takes the id and returns the leader of id's team. Used for collab tasks. Returns none if not found."""
    async with get_session() as session:
        stmt = select(Teams.leader).filter(
            (Teams.leader == id) | (Teams.user2 == id) |(Teams.user3 == id) | (Teams.user4 == id))
        result = await session.execute(stmt)
        leader = result.scalars().first()
        return leader




def calculate_winnings(num_emojis, slot_number, constant=3):
    probability = 1 / (num_emojis ** (slot_number - 1))
    winnings = constant * slot_number * (1 / probability)
    return int(winnings)

def get_file_types(attachments):
    file_list = []
    for file in attachments:
        file_list.append(file.filename.rpartition(".")[-1])
    file_tuples = enumerate(file_list)
    # Check for uniqueness by assigning index to dictionary
    # Iterates over dictionary to find if an index has been assigned
    file_dict = {}
    for index, filetype in file_tuples:
        if filetype not in file_dict:
            file_dict[filetype] = index
    return file_dict


def hash_file(filename: str):
    """Hashes a file's contents

    Args:
        filename (str): Path to a file

    Returns:
        _Hash: The file contents' hash
    """
    with open(filename, 'rb', buffering=0) as f:
        return hashlib.file_digest(f, 'sha256')

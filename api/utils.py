import hashlib
import os
import uuid
from urllib.parse import urlparse
import requests
from discord.ext import commands
from sqlalchemy import select, insert, update
from api.db_classes import Money, Tasks, HostRole, session
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64
DOWNLOAD_DIR = os.getenv('DOWNLOAD_DIR')
DB_DIR = os.getenv('DB_DIR')


def get_balance(user_id, guild):
    money = session.scalars(select(Money.coins).where(Money.user_id == user_id)).first()
    if money is None:
        balance = 100
        print(guild)
        stmt = (insert(Money).values(guild=guild, user_id=user_id, coins=balance))
        session.execute(stmt)
        session.commit()
    else:
        balance = money
    return balance


def update_balance(user_id, guild, new_balance):
    stmt = (update(Money).values(guild=guild, user_id=user_id, coins=new_balance).where(Money.user_id == user_id))
    session.execute(stmt)
    session.commit()


def add_balance(user_id, server_id, amount):
    current_balance = get_balance(user_id, server_id)
    new_balance = current_balance + amount
    update_balance(user_id, server_id, new_balance)


def deduct_balance(user_id, guild, amount):
    current_balance = get_balance(user_id, guild)
    new_balance = max(current_balance - amount, 0)  # Ensure balance doesn't go negative
    update_balance(user_id, guild, new_balance)


def get_host_role(guild_id):
    default = DEFAULT
    """Retrieves the host role. By default, on the server, the default host role is 'Host'."""
    host_role = session.scalars(select(HostRole.role_id).where(HostRole.comp == default and HostRole.guild_id == guild_id)).first()

    if host_role:
        print(host_role)
        return host_role
    else:
        return None # default host role name.


def has_host_role():
    async def predicate(ctx):
        role = get_host_role(ctx.message.guild.id)
        # Check if the role is a name
        has_role = ctx.author.get_role(role) is not None
        return has_role

    return commands.check(predicate)


async def download_from_url(url) -> str:
    try:
        url_parsed = urlparse(url)
        filename, file_extension = os.path.splitext(os.path.basename(url_parsed.path))
        file_path = os.path.join(DOWNLOAD_DIR, f"{filename}{file_extension}")

        file = requests.get(url)
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
    if seconds < 0:
        print("Seconds cannot be negative.")
        return

    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    time_str = f"{minutes}:{remaining_seconds:06.3f}"
    return time_str


def is_task_currently_running():
    """Check if a task is currently running"""
    # Is a task running?
    # Does this need to be a function even?
    active = session.scalars(select(Tasks.is_active).where(Tasks.is_active == 1)).first()
    return active


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

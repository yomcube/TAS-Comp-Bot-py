import os
import struct
import uuid
import discord
from discord.ext import commands
import json
import sqlite3

from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64

def get_host_role():
    """Retrieves the host role. By default, on the server, the default host role is 'Host'."""
    connection = sqlite3.connect("./database/settings.db")
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM host_role WHERE comp = ?",
                   (DEFAULT,))  # chooses default in dotenv
    role = cursor.fetchone()

    if role:
        host_role = role[1]
        connection.close()
        return host_role
    else:
        connection.close()
        return "Host"  # default host role name.


def has_host_role():
    async def predicate(ctx):
        role = get_host_role()
        # Check if the role is a name
        has_role = discord.utils.get(ctx.author.roles, name=role) is not None
        return has_role

    return commands.check(predicate)


async def download_attachments(attachments, file_name=None) -> str:
    # TODO: Prematurely handle Directory missing error
    if len(file_name) == 0:
        file_name = str(uuid.uuid4())
    for attachment in attachments:
        file_type = attachment.filename.split(".")[-1]
        file_path = f"download/{file_name}.{file_type}"
        file = open(file_path, "w")  # changed this from x to w, because as submitters, we can submit multiple times
        await attachment.save(fp=file_path)
        file.close()
    return file_name


async def check_json_guild(file, guild_id):  # TODO: Normalise file handling, rename function
    with open(file, "r") as f:

        data = json.loads(f.read())
        for guild in data:
            if guild == guild_id:
                return True

    return False


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


def get_lap_time(rkg):
    """Retrieves the lap times of all laps of a given RKG file"""
    # Check if compressed and remove potential CTGP data
    if (rkg[12] & 0x08) == 0x08:
        rkg_length = struct.unpack('>I', rkg[0x88:0x8C])[0] + 0x90
        rkg = rkg[:rkg_length]

    # Extract the number of laps
    nr_laps = rkg[0x10]
    lap_times = []
    for i in range(nr_laps):
        min = rkg[0x11 + i * 3] >> 1
        sec = ((rkg[0x11 + i * 3] & 0x1) << 6) | (rkg[0x12 + i * 3] >> 2)
        mil = ((rkg[0x12 + i * 3] & 0x3) << 8) | rkg[0x13 + i * 3]
        lap_times.append(f"{min}:{sec:02}.{mil:03}")
    return lap_times


def is_task_currently_running():
    """Check if a task is currently running"""
    connection = sqlite3.connect("./database/tasks.db")
    cursor = connection.cursor()

    # Is a task running?
    cursor.execute("SELECT * FROM tasks WHERE is_active = 1")
    currently_running = cursor.fetchone()
    connection.close()
    return currently_running


def get_balance(username):
    connection = sqlite3.connect("./database/economy.db")
    cursor = connection.cursor()
    cursor.execute("SELECT coins FROM slots WHERE username = ?", (username,))
    result = cursor.fetchone()
    if result is None:
        cursor.execute("INSERT INTO slots (username, coins) VALUES (?, ?)", (username, 100))
        connection.commit()
        balance = 100
    else:
        balance = result[0]
    connection.close()
    return balance


def update_balance(username, new_balance):
    connection = sqlite3.connect("./database/economy.db")
    cursor = connection.cursor()
    cursor.execute("UPDATE slots SET coins = ? WHERE username = ?", (new_balance, username))
    connection.commit()
    connection.close()


def add_balance(username, amount):
    current_balance = get_balance(username)
    new_balance = current_balance + amount
    update_balance(username, new_balance)


def deduct_balance(username, amount):
    current_balance = get_balance(username)
    new_balance = max(current_balance - amount, 0)  # Ensure balance doesn't go negative
    update_balance(username, new_balance)


def calculate_winnings(num_emojis, slot_number, constant=3):
    probability = 1 / (num_emojis ** (slot_number - 1))
    winnings = constant * slot_number * (1 / probability)
    return int(winnings)


def get_file_types(attachments):
    file_list = []
    for file in attachments:
        file_list.append(file.filename.partition(".")[-1])
    file_tuples = enumerate(file_list, start=1)
    # Check for uniqueness by assigning index to dictionary
    # Iterates over dictionary to find if an index has been assigned
    file_dict = {}
    for index, filetype in file_tuples:
        if filetype not in file_dict:
            file_dict[filetype] = index
    return file_dict


tracks = ["Luigi Circuit", "Moo Moo Meadows", "Mushroom Gorge", "Toad's Factory", "Mario Circuit", "Coconut Mall",
          "DK Summit", "Wario's Gold Mine", "Daisy Circuit", "Koopa Cape", "Maple Treeway", "Grumble Volcano",
          "Dry Dry Ruins", "Moonview Highway", "Bowser's Castle", "Rainbow Road", "GCN Peach Beach", "DS Yoshi Falls",
          "SNES Ghost Valley 2", "N64 Mario Raceway", "N64 Sherbet Land", "GBA Shy Guy Beach", "DS Delfino Square",
          "GCN Waluigi Stadium", "DS Desert Hills", "GBA Bowser Castle 3", "N64 DK's Jungle Parkway",
          "GCN Mario Circuit", "SNES Mario Circuit 3", "DS Peach Gardens", "GCN DK Mountain", "N64 Bowser's Castle"]
tracks_abbreviated = ['LC', 'MMM', 'MG', 'TF', 'MC', 'CM', 'DKSC', 'WGM', 'DC', 'KC', 'MT', 'GV', 'DDR', 'MH', 'BC',
                      'RR', 'rPB', 'rYF', 'rGV2', 'rMR', 'rSL', 'rSGB', 'rDS', 'rWS', 'rDH', 'rBC3', 'rDKJP', 'rMC',
                      'rMC3', 'rPG', 'rDKM', 'rBC']

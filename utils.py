import uuid
import msgspec as ms
import sqlite3

async def download_attachments(attachments, file_name=None) -> str:
    # TODO: Prematurely handle Directory missing error
    if len(file_name) == 0:
        file_name = str(uuid.uuid4())
    for attachment in attachments:
        file_type = attachment.filename.split(".")[-1]
        file_path = f"database/{file_name}.{file_type}"
        file = open(file_path, "w") # changed this from x to w, because as submitters, we can submit multiple times
        await attachment.save(fp=file_path)
        file.close()
    return file_name


async def check_json_guild(file, guild_id):     # TODO: Normalise file handling, rename function
    with open(file, "r") as f:

        data = ms.json.decode(f.read())
        for guild in data:
            if guild == guild_id:
                return True

    return False

def get_balance(username):
    connection = sqlite3.connect("database/economy.db")
    cursor = connection.cursor()
    cursor.execute("SELECT coins FROM slots WHERE username = ?", (username))
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
    connection = sqlite3.connect("database/economy.db")
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

def calculate_winnings(num_emojis, slot_number, base_amount=10):
    probability = 1 / (num_emojis ** slot_number)
    winnings = base_amount * (1 / probability)
    return int(winnings)


tracks = [ "Luigi Circuit", "Moo Moo Meadows", "Mushroom Gorge", "Toad's Factory", "Mario Circuit", "Coconut Mall", "DK Summit", "Wario's Gold Mine", "Daisy Circuit", "Koopa Cape", "Maple Treeway", "Grumble Volcano", "Dry Dry Ruins", "Moonview Highway", "Bowser's Castle", "Rainbow Road", "GCN Peach Beach", "DS Yoshi Falls", "SNES Ghost Valley 2", "N64 Mario Raceway", "N64 Sherbet Land", "GBA Shy Guy Beach", "DS Delfino Square", "GCN Waluigi Stadium", "DS Desert Hills", "GBA Bowser Castle 3", "N64 DK's Jungle Parkway", "GCN Mario Circuit", "SNES Mario Circuit 3", "DS Peach Gardens", "GCN DK Mountain", "N64 Bowser's Castle" ]
tracks_abbreviated = [ 'LC', 'MMM', 'MG', 'TF', 'MC', 'CM', 'DKSC', 'WGM', 'DC', 'KC', 'MT', 'GV', 'DDR', 'MH', 'BC', 'RR', 'rPB', 'rYF', 'rGV2', 'rMR', 'rSL', 'rSGB', 'rDS', 'rWS', 'rDH', 'rBC3', 'rDKJP', 'rMC', 'rMC3', 'rPG', 'rDKM', 'rBC' ]
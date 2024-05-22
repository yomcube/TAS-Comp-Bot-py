import uuid
import msgspec as ms
import sqlite3

def connect_tasks():
    # TODO: Save table in database folder instead of root
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()
    cursor.execute("""CREATE TABLE tasks (
                        task INTEGER, 
                        year INTEGER, 
                        is_active INTEGER
                        )""")
    connection.commit()
    connection.close()


async def download_attachments(attachments, file_name=None) -> str:
    # TODO: Prematurely handle Directory missing error
    if len(file_name) == 0:
        file_name = str(uuid.uuid4())
    for attachment in attachments:
        file_type = attachment.filename.split(".")[-1]
        file_path = f"database/{file_name}.{file_type}"
        file = open(file_path, "x")
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


tracks = [ "Luigi Circuit", "Moo Moo Meadows", "Mushroom Gorge", "Toad's Factory", "Mario Circuit", "Coconut Mall", "DK Summit", "Wario's Gold Mine", "Daisy Circuit", "Koopa Cape", "Maple Treeway", "Grumble Volcano", "Dry Dry Ruins", "Moonview Highway", "Bowser's Castle", "Rainbow Road", "GCN Peach Beach", "DS Yoshi Falls", "SNES Ghost Valley 2", "N64 Mario Raceway", "N64 Sherbet Land", "GBA Shy Guy Beach", "DS Delfino Square", "GCN Waluigi Stadium", "DS Desert Hills", "GBA Bowser Castle 3", "N64 DK's Jungle Parkway", "GCN Mario Circuit", "SNES Mario Circuit 3", "DS Peach Gardens", "GCN DK Mountain", "N64 Bowser's Castle" ]
tracks_abbreviated = [ 'LC', 'MMM', 'MG', 'TF', 'MC', 'CM', 'DKSC', 'WGM', 'DC', 'KC', 'MT', 'GV', 'DDR', 'MH', 'BC', 'RR', 'rPB', 'rYF', 'rGV2', 'rMR', 'rSL', 'rSGB', 'rDS', 'rWS', 'rDH', 'rBC3', 'rDKJP', 'rMC', 'rMC3', 'rPG', 'rDKM', 'rBC' ]
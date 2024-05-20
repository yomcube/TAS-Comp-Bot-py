from dotenv import load_dotenv
import os
import uuid
import msgspec as ms

load_dotenv()
download_dir = os.getenv('DOWNLOAD_DIR')


async def download_attachments(attachments, file_name=None) -> str:
    # TODO: Prematurely handle Directory missing error
    if len(file_name) == 0:
        file_name = str(uuid.uuid4())
    for attachment in attachments:
        file_type = attachment.filename.split(".")[-1]
        file_path = f"{download_dir}/{file_name}.{file_type}"
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

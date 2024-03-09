from dotenv import load_dotenv
import os
import uuid

load_dotenv()
download_dir = os.getenv('DOWNLOAD_DIR')


async def handle_dm_attachments(attachments, *gog):
    # Handle up to two attachments
    attachments = attachments[:2]
    await download_attachments(attachments)


async def download_attachments(attachments, *name) -> str:
    # TODO: Prematurely handle Directory missing error
    if len(name) == 0:
        name = str(uuid.uuid4())
    for attachment in attachments:
        file_type = attachment.filename.split(".")[-1]
        file_path = f"{download_dir}/{name}.{file_type}"
        with open(file_path, "x") as file:
            await attachment.save(fp=file_path)
    return name

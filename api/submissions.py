from api.utils import download_attachments


async def handle_submissions(message):
    attachments = message.attachments
    # TODO: Detect which comp, to limit number of files
    attachments = attachments[:2]
    prefix = ""
    num = ""
    file_name = f"{prefix}Task{num}By{message.author.name}"
    name = await download_attachments(attachments, file_name)


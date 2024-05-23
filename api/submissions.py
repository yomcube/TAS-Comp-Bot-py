from utils import download_attachments


async def handle_submissions(message, file, num, year):
    attachments = message.attachments
    # TODO: Detect which comp, to limit number of files
    attachments = attachments[:2]
    if file == "rkg":
        file_name = f"Task{num}-{year}By{message.author.display_name}"
        await download_attachments(attachments, file_name)
    elif file == "rksys":
        file_name = f"Task{num}-{year}By{message.author.display_name}_rksys"
        await download_attachments(attachments, file_name)


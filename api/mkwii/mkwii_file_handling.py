from api.submissions import handle_submissions, first_time_submission
from api.utils import is_task_currently_running, readable_to_float
from api.mkwii.mkwii_utils import get_lap_time
from api.db_classes import session, Submissions
from sqlalchemy import insert, update


async def handle_mkwii_files(message, attachments, file_dict, self):
    current_task = await is_task_currently_running()

    if file_dict.get("rkg") is not None:
        index = file_dict.get("rkg")

        if current_task:

            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`.rkg` file detected!\nThe file was successfully saved. "
                "Type `$info` for more information about the file.")

            # handle submission
            await handle_submissions(message, self)

            # retrieving lap time, to estimate submission time

            rkg_data = await attachments[0].read()

            try:
                rkg = bytearray(rkg_data)
                if rkg[:4] == b'RKGD':
                    lap_times = get_lap_time(rkg)

                # float time to upload to db
                time = readable_to_float(lap_times[0])
                # For most (but not all) mkw single-track tasks, the first lap time is usually the
                # time of the submission, given the task is on lap 1 and not backwards.

            except UnboundLocalError:
                # This exception catches blank rkg files
                time = 0
                await message.channel.send("Nice blank rkg there")

            # Add first-time submission
            if first_time_submission(message.author.id):  # seems odd to check in function, queries db twice
                # Assuming the table `submissions` has columns: task, name, id, url, time, dq, dq_reason
                await session.execute(insert(Submissions).values(task=current_task[0], name=message.author.name,
                                                                 user_id=message.author.id,
                                                                 url=attachments[index].url, time=time, dq=0,
                                                                 dq_reason=''))
                await session.commit()

            # If not first submission: replace old submission
            else:
                await session.execute(update(Submissions).values(url=attachments[index].url, time=time).where(
                    Submissions.user_id == message.author.id))
                await session.commit()
        # No ongoing task
        else:
            await message.channel.send("There is no active task yet.")

    #################################
    # recognition of rksys submission
    #################################

    elif file_dict.get("dat"):
        index = file_dict.get("dat")
        if current_task:

            # handle submission
            await handle_submissions(message, self)

            # Add first-time submission
            if first_time_submission(message.author.id):
                await session.execute(insert(Submissions).values(task=current_task[0], name=message.author.name,
                                                                 user_id=message.author.id,
                                                                 url=attachments[index].url, time=0, dq=0,
                                                                 dq_reason=''))

            # If not first submission: replace old submission
            else:
                await session.execute(update(Submissions).values(url=attachments[index].url)
                                      .where(Submissions.user_id == message.author.id))

            await session.commit()
            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`rksys.dat` detected!\nThe file was successfully saved. Type `$info` for more information about the "
                "file.")

        else:
            await message.channel.send("There is no active task.")

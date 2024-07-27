from api.submissions import handle_submissions, first_time_submission
from api.utils import is_task_currently_running, readable_to_float, get_team_size, is_in_team, get_leader
from api.nsmbwii.nsmbwii_utils import get_vi_count
from api.db_classes import get_session, Submissions, Teams, Userbase
from sqlalchemy import insert, update, select
from struct import unpack


async def handle_nsmbwii_files(message, attachments, file_dict, self):
    current_task = await is_task_currently_running()

    if file_dict.get("dtm") is not None:
        index = file_dict.get("dtm")

        if current_task:

            # handle submission
            await handle_submissions(message, self)

            # retrieving lap time, to estimate submission time

            dtm_data = await attachments[0].read()

            try:
                dtm = bytearray(dtm_data)
                if dtm[:4] == b'DTM\x1A':
                    vi_count = unpack('<L', dtm[0xD:0x11])[0]

                # float time to upload to db
                time = vi_count / 60

            except UnboundLocalError:
                # This exception catches blank dtm files
                time = 0
                await message.channel.send("Nice blank dtm there")

            ###########################
            # Who are we submitting as
            ###########################
            submitter_name = message.author.name
            submitter_id = message.author.id

            # If submitter is in a team, make any submission on behalf of his leader
            async with get_session() as session:
                if await get_team_size() > 1 and await is_in_team(submitter_id):
                    submitter_id = await get_leader(submitter_id)
                    submitter_name = await session.scalar(select(Userbase.user).where(Userbase.user_id == submitter_id))

            ####################
            # Adding submission
            ####################

            # first time submission (within the task)
            if await first_time_submission(submitter_id):
                    await session.execute(insert(Submissions).values(task=current_task[0], name=submitter_name,
                                                                     user_id=submitter_id,
                                                                     url=attachments[index].url, time=time, dq=0,
                                                                     dq_reason=''))
                    await session.commit()

            # If not first submission: replace old submission
            else:
                async with get_session() as session:
                    await session.execute(update(Submissions).values(url=attachments[index].url, time=time)
                                          .where(Submissions.user_id == submitter_id))
                    await session.commit()

            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`.dtm` file detected!\nThe file was successfully saved. "
                "Type `$info` for more information about the file.")

        # No ongoing task
        else:
            await message.channel.send("There is no active task yet.")


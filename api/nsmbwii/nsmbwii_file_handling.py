from struct import unpack

from sqlalchemy import insert, update, select

from api.db_classes import get_session, Submissions, Userbase
from api.submissions import handle_submissions, first_time_submission
from api.utils import is_task_currently_running, get_team_size, is_in_team, get_leader
from commands.db.requesttask import has_requested_already, is_time_over


async def handle_nsmbwii_files(message, attachments, file_dict, self):
    current_task = await is_task_currently_running()

    if file_dict.get("dtm") is not None:

        if current_task:
            ##################################################
            # Cases where someone is denied submission
            ##################################################

            # Speed task: Has not requested task, or time is over
            is_speed_task = (await is_task_currently_running())[4]
            is_released = (await is_task_currently_running())[7]

            if is_speed_task:
                if not (await has_requested_already(message.author.id)) and not is_released:
                    await message.channel.send("You may not submit yet! Use `$requesttask` first.")
                    return

                if await is_time_over(message.author.id):
                    # If they have not submitted, they get a different message.
                    async with get_session() as session:
                        query = select(Submissions.user_id).where(Submissions.user_id == message.author.id)
                        result = (await session.execute(query)).first()


                        if result is None:
                            message_to_send = ("You can't submit, your time is up! If you wish to send in a late submission, "
                                       "please DM the current host so they can add your submission manually.")

                        else:
                            message_to_send = "You can't submit, your time is up!"


                    await message.channel.send(message_to_send)
                    return

            ##################################################
            # Otherwise continue
            ##################################################

            # handle submission
            await handle_submissions(message, self)

            # retrieving lap time, to estimate submission time

            dtm_data = await attachments[0].read()

            try:
                dtm = bytearray(dtm_data)
                vi_count = 0
                if dtm[:4] == b'DTM\x1A':
                    vi_count = unpack("<Q", dtm[0xD:0x15])[0]

                # float time to upload to db
                time = vi_count

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

            url = " ".join(a.url for a in attachments)

            # Hacky, but the character is set with the DTM bytes so
            # another field doesn't have to be added to the DB

            # first time submission (within the task)
            if await first_time_submission(submitter_id):
                async with get_session() as session:
                    await session.execute(insert(Submissions).values(task=current_task[0], name=submitter_name,
                                                                     user_id=submitter_id,
                                                                     url=url, time=time, character=dtm,
                                                                     dq=0, dq_reason=''))
                    await session.commit()

            # If not first submission: replace old submission
            else:
                async with get_session() as session:
                    await session.execute(update(Submissions).values(url=url, time=time, character=dtm)
                                          .where(Submissions.user_id == submitter_id))
                    await session.commit()

            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`.dtm` file detected!\nThe file was successfully saved.")

        # No ongoing task
        else:
            await message.channel.send("There is no active task.")

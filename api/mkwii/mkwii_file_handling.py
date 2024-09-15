from api.submissions import handle_submissions, first_time_submission
from api.utils import is_task_currently_running, readable_to_float, get_team_size, is_in_team, get_leader, is_task_currently_running
from api.mkwii.mkwii_utils import get_lap_time, get_character, get_vehicle
from commands.db.requesttask import has_requested_already, is_time_over
from api.db_classes import get_session, Submissions, Teams, Userbase
from sqlalchemy import insert, update, select


async def handle_mkwii_files(message, attachments, file_dict, self):
    current_task = await is_task_currently_running()

    if file_dict.get("rkg") is not None:
        index = file_dict.get("rkg")

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
                            message_to_send = (f"You can't submit, your time is up! If you wish to send in a late submission, "
                                       f"please DM the current host so they can add your submission manually.")

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

            rkg_data = await attachments[0].read()

            try:
                rkg = bytearray(rkg_data)
                if rkg[:4] == b'RKGD':
                    lap_times = get_lap_time(rkg)

                # float time to upload to db
                time = readable_to_float(lap_times[0])
                # For most (but not all) mkw single-track tasks, the first lap time is usually the
                # time of the submission, given the task is on lap 1 and not backwards.

                character = get_character(rkg)
                vehicle = get_vehicle(rkg)

            except UnboundLocalError:
                # This exception catches blank rkg files
                time = 0
                character = None
                vehicle = None
                await message.channel.send("Nice blank rkg there")

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

            ###################
            # Adding submission
            ####################

            # first time submission (within the task)
            if await first_time_submission(submitter_id):
                async with get_session() as session:
                    await session.execute(insert(Submissions).values(task=current_task[0], name=submitter_name,
                                                                     user_id=submitter_id,
                                                                     url=attachments[index].url, time=time, dq=0,
                                                                     dq_reason='', character=character,
                                                                     vehicle=vehicle))
                    await session.commit()

            # If not first submission: replace old submission
            else:
                async with get_session() as session:
                    await session.execute(update(Submissions).values(url=attachments[index].url, time=time,
                                                                     character=character,
                                                                     vehicle=vehicle)
                                          .where(Submissions.user_id == submitter_id))
                    await session.commit()

            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`.rkg` file detected!\nThe file was successfully saved. "
                "Type `$info` for more information about the file.")

        # No ongoing task
        else:
            await message.channel.send("There is no active task yet.")

    #################################################
    # recognition of rksys submission
    #################################################

    elif file_dict.get("dat") is not None:
        index = file_dict.get("dat")
        if current_task:

            if current_task:
                ##################################################
                # Cases where someone is denied submission
                ##################################################

                # Speed task: Has not requested task, or time is over
                is_speed_task = (await is_task_currently_running())[4]
                is_released = (await is_task_currently_running())[7]

                if is_speed_task:
                    if not await has_requested_already(message.author.id) and not is_released:
                        await message.channel.send("You may not submit yet! Use $requesttask first.")
                        return

                    if await is_time_over(message.author.id):
                        await message.channel.send("You can't submit, your time is already over!")
                        return

            # handle submission
            await handle_submissions(message, self)

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

            # Add first-time submission
            if await first_time_submission(message.author.id):
                async with get_session() as session:
                    await session.execute(insert(Submissions).values(task=current_task[0], name=submitter_name,
                                                                     user_id=submitter_id,
                                                                     url=attachments[index].url, time=0, dq=0,
                                                                     dq_reason='', character="48", vehicle="36"))
                    # I defined 48 and 36 as being none

            # If not first submission: replace old submission
            else:
                async with get_session() as session:
                    await session.execute(update(Submissions).values(url=attachments[index].url, time=0,
                                                                     character="48", vehicle="36")
                                          .where(Submissions.user_id == submitter_id))

                    await session.commit()

            # Tell the user the submission has been received
            print(f"File received!\nBy: {message.author}\nMessage sent: {message.content}")
            await message.channel.send(
                "`rksys.dat` detected!\nThe file was successfully saved. Type `$info` for more information about the "
                "file.")


        else:
            await message.channel.send("There is no active task.")
import discord
import os
import shared
from dotenv import load_dotenv
from api.db_classes import SubmissionChannel, Userbase, get_session, Submissions, LogChannel, SeekingChannel, Teams
from sqlalchemy import insert, select, or_
from api.utils import get_file_types, get_leader, get_team_size, is_in_team, get_submitter_role, is_task_currently_running
from api.dm_handlers import handlers_dict, init_dm_handlers

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

if DEFAULT == 'mkw':
    guild_id = 1214800758881394718
elif DEFAULT == 'nsmbw':
    guild_id = 1238999592947810366


async def get_submission_channel(comp):
    async with get_session() as session:
        query = select(SubmissionChannel.channel_id).where(SubmissionChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No submission channel found for competition '{comp}'.")
            return None
        return channel[0]


async def get_submission_channel_guild(channel_id):
    async with get_session() as session:
        query = select(SubmissionChannel.guild_id).where(SubmissionChannel.channel_id == channel_id)
        guild_id = (await session.scalars(query)).first()
        if guild_id is None:
            return None
        return guild_id


async def get_logs_channel(comp):
    async with get_session() as session:
        query = select(LogChannel.channel_id).where(LogChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No logging channel found for '{comp}'.")
            return None
        return channel[0]


async def get_seeking_channel(comp):
    async with get_session() as session:
        query = select(SeekingChannel.channel_id).where(SeekingChannel.comp == comp)
        channel = (await session.execute(query)).first()  # there should only be 1 entry per table per competition
        # Handle case where no rows are found in the database
        if channel is None or channel[0] is None:
            print(f"No seeking channel found for '{comp}'.")
            return None
        return channel[0]




async def first_time_submission(user_id):
    """Check if a certain user id has submitted to this competition already"""
    async with get_session() as session:
        query = select(Submissions.user_id).where(Submissions.user_id == user_id)
        result = (await session.execute(query)).first()

        return not result


async def new_competitor(user_id):
    """Checks if a competitor has EVER submitted (present and past tasks)."""
    async with get_session() as session:
        query = select(Userbase.user_id).where(Userbase.user_id == user_id)
        result = (await session.execute(query)).first()
        return not result


async def get_display_name(user_id):
    """Returns the display name of a certain user ID."""
    async with get_session() as session:
        result = (await session.scalars(select(Userbase.display_name).where(Userbase.user_id == user_id))).first()
        return result

async def get_team_name(user_id):
    """Returns the display name of the team a certain user ID is in."""
    async with get_session() as session:
        stmt = select(Teams.team_name).filter(
            (Teams.leader == user_id) | (Teams.user2 == user_id) | (Teams.user3 == user_id) |
            (Teams.user4 == user_id))

        result = (await session.execute(stmt)).first()
        return result[0] if result else None
async def get_team_ids(id):
    """Takes list of IDs, and retrieves all the members of the team. Used for submission list"""
    async with get_session() as session:
        # Construct the query to find the team with the specified user ID
        result = await session.execute(
            select(Teams).where(
                or_(Teams.leader == id, Teams.user2 == id, Teams.user3 == id, Teams.user4 == id)
            )
        )
        team = result.scalars().first()

        if team:
            # Filter out None values and return the list of user IDs
            return [user for user in [team.leader, team.user2, team.user3, team.user4] if user is not None]
        else:
            return None


async def get_team_members(id_list):
    """Takes list of IDs, and retrieves all the members of the team. Used for submission list"""
    Members = []
    for id in id_list:
        name = await get_display_name(id)
        Members.append(name)
    return Members


async def count_submissions():
    """Counts the number of submissions in the current task."""
    async with get_session() as session:
        query = select(Submissions)
        result = (await session.scalars(query)).fetchall()
        return len(result)

async def post_submission_list(channel, id, name):
    # Case if user is in team
    if await is_in_team(id):
        ids = await get_team_ids(id)
        members = await get_team_members(ids)
        team_name = await get_team_name(id)
        mentions = ' '.join([f'<@{user_id}>' for user_id in ids])

<<<<<<< Updated upstream
        return await channel.send(
            f"**__Current Submissions:__**\n1. {team_name} ({' & '.join(members)}) ||{mentions}||",
            allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
=======
        # No ( ) if no team name
        if team_name == None:
            return await channel.send(
                f"**__Current Submissions:__**\n1. {' & '.join(members)} ||{mentions}||",
                allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)

        else:
            return await channel.send(
                f"**__Current Submissions:__**\n1. {team_name} ({' & '.join(members)}) ||{mentions}||",
                allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)
>>>>>>> Stashed changes

    # Case if solo
    return await channel.send(
        f"**__Current Submissions:__**\n1. {name} ||<@{id}>||",
        allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)


async def update_submission_list(last_message, id, name):
    """Handles updating the submission list message and renaming user submissions"""
    # Case if user is in team
    if await is_in_team(id):
        ids = await get_team_ids(id)
        members = await get_team_members(ids)
        team_name = await get_team_name(id)
        mentions = ' '.join([f'<@{user_id}>' for user_id in ids])

        # No ( ) if no team name
        if team_name == None:
            new_content = (f"{last_message.content}\n{(await count_submissions()) + 1}. {' & '.join(members)} ||{mentions}||")


        # Case if they actually set a team name
        else:
            new_content = (f"{last_message.content}\n{(await count_submissions()) + 1}. {team_name} ({' & '.join(members)})"
                       f" ||{mentions}||")


        return await last_message.edit(content=new_content)

    # solo submission
    new_content = (f"{last_message.content}\n{await count_submissions()}. {name}"
                    f" ||<@{id}>||")
    return await last_message.edit(content=new_content)


async def generate_submission_list(self):
    """ Edits the submission list in the submission channel.
        Takes bot (self) as an argument -- so that the bot may retrieve the channel & message.
    """
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)
    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            message_to_edit = message


    async with get_session() as session:

        active_task = (await session.scalars(select(Submissions.task))).first()
        submissions = (await session.scalars(select(Submissions).where(Submissions.task == active_task)))
        formatted_submissions = "**__Current Submissions:__**"

        # Update submission list for a solo submission
        for submission in submissions:
            if not await is_in_team(submission.user_id):
                formatted_submissions += f"\n{submission.index}. {await get_display_name(submission.user_id)} ||<@{submission.user_id}>||"


            # Generate submission list for a team submission
            else:
                ids = await get_team_ids(submission.user_id)
                members = await get_team_members(ids)
                team_name = await get_team_name(submission.user_id)
                mentions = ' '.join([f'<@{user_id}>' for user_id in ids])

                # No ( ) if they have no special team name
                if team_name == None:
                    formatted_submissions += f"\n{submission.index}. {' & '.join(members)} ||{mentions}||"

                # Case if they actually set a team name
                else:
                    formatted_submissions += (
                        f"\n{submission.index}. {team_name} ({' & '.join(members)}) ||{mentions}||"
                    )


    return await message_to_edit.edit(content=formatted_submissions)



async def handle_submissions(message, self):
    author = message.author
    author_name = message.author.name
    author_id = message.author.id
    author_dn = message.author.display_name

    ##################################################
    # Adding submission to submission list channel
    ##################################################
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    # Checking if submitter has ever participated before
    if await new_competitor(author_id):
        # adding him to the user database.
        async with get_session() as session:
            await session.execute(insert(Userbase).values(user_id=author_id, user=author_name, display_name=author_dn))
            await session.commit()

    if not channel:
        print("Could not find the channel.")
        return

    async for msg in channel.history(limit=5):
        last_message = msg
        if last_message.author == self.bot.user:
            break
    else:
        last_message = None

    # Determine the correct author_id and display_name
    if await get_team_size() > 1 and await is_in_team(author_id):
        author_id = await get_leader(author_id)
    author_display_name = await get_display_name(author_id)

    # New entry to the list in #submissions
    if last_message:

        # Add a new line only if it's a new user ID submitting
        if await first_time_submission(author_id):

                await update_submission_list(last_message, author_id, author_display_name)


    else:
        # There are no submissions (brand-new task); send a message on the first submission
        await post_submission_list(channel, author_id, author_display_name)

    ##################################################################
    # Adding submitter role to submitters (if not speed task)
    ##################################################################
    if not (await is_task_currently_running())[4]: # if not speed task

        guild_id = shared.main_guild.id

        if guild_id is None:
            print("Guild not detected yet.")
            return

        submitter_role = await get_submitter_role(DEFAULT)

        # Fetch the member from the detected guild
        server = self.bot.get_guild(guild_id)
        member = server.get_member(author_id)

        if member:
            role = server.get_role(submitter_role)
            if role:
                if role not in member.roles:
                    await member.add_roles(role)
                    print(f"Role {role.name} has been assigned to {member.display_name}.")
            else:
                await message.channel.send(f"Role with ID {submitter_role} not found in this server.")
        else:
            await message.channel.send(f"User with ID {author_id} not found in this server.")


async def handle_dms(message, self):
    author = message.author
    author_dn = message.author.display_name

    if isinstance(message.channel, discord.DMChannel) and author != self.bot.user:

        # log all DMs to a set channel
        channel = self.bot.get_channel(await get_logs_channel(DEFAULT))
        attachments = message.attachments
        if channel:
            await channel.send(f"Message from {author_dn}: {message.content} " +
                                " ".join([attachment.url for attachment in message.attachments if message.attachments]),
                                allowed_mentions=discord.AllowedMentions.none(), suppress_embeds=True)

        #########################
        # Recognizing submission
        #########################

        if len(attachments) > 0:
            file_dict = get_file_types(attachments)
            try:
                await handlers_dict[DEFAULT](message, attachments, file_dict, self)
            
            except KeyError:
                print(f"Could not find DM handler for '{DEFAULT}'.")
            except TimeoutError:
                await channel.send("Could not process Files!")

init_dm_handlers()

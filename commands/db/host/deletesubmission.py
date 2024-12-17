import discord
from discord.ext import commands
from api.utils import has_host_role
from api.db_classes import Submissions, get_session, Tasks
from api.submissions import get_submission_channel, get_display_name, generate_submission_list
from sqlalchemy import select, delete
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def remove_from_submission_list(self, name_to_remove):
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            lines = message.content.split('\n')
            new_lines = [lines[0]]  # Preserve the first line as is ("Current submissions")

            for line in lines[1:]:
                if name_to_remove not in line:
                    new_lines.append(line)

            new_content = '\n'.join(new_lines)
            if new_content != message.content:
                await message.edit(content=new_content)
            break  # Stop after finding the last bot message


class DeleteSubmission(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="delete-submission", description="Delete someone's submission", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, user: discord.Member):
        async with get_session() as session:
            currently_running = (await session.execute(select(Tasks).where(Tasks.is_active == 1))).first()
            if not currently_running:
                return await ctx.send("There is no ongoing task")

        async with get_session() as session:
            data = (await session.scalars(select(Submissions).where(Submissions.user_id == user.id))).first()

        if data is None:
            return await ctx.reply(f"{user} has no submission.")

        # Delete submission from db
        async with get_session() as session:
            await session.execute(delete(Submissions).where(Submissions.user_id == user.id))
            await session.commit()



        # Get the submission list channel, and update the submission list with the new name
        submission_channel = await get_submission_channel(DEFAULT)
        channel = self.bot.get_channel(submission_channel)
        async for message in channel.history(limit=3):
            # Check if the message was sent by the bot
            if message.author == self.bot.user:
                message_to_edit = message
        await generate_submission_list(message_to_edit)


        await ctx.send(f"{user.display_name}'s submission has been deleted.")


async def setup(bot) -> None:
    await bot.add_cog(DeleteSubmission(bot))

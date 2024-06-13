from discord.ext import commands

from api.db_classes import Userbase
from api.submissions import get_submission_channel
from api.utils import session
from sqlalchemy import select, update
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def rename_in_submission_list(self, old_display_name, new_display_name):
    submission_channel = get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            lines = message.content.split('\n')
            new_lines = [lines[0]]  # Preserve the first line as is ("Current submissions")

            # Check if the new display name is already in use in the rest of the lines
            for line in lines[1:]:
                if new_display_name in line:
                    return

            for line in lines[1:]:
                if old_display_name in line:
                    line = line.replace(old_display_name, new_display_name)
                new_lines.append(line)

            new_content = '\n'.join(new_lines)
            if new_content != message.content:
                await message.edit(content=new_content)
            break  # Stop after finding the last bot message


class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list", with_app_command=True)
    async def command(self, ctx, *, new_name):

        if '@' in new_name:
            return await ctx.reply("You may not use @ in your name.")

        if len(new_name) > 120:
            return await ctx.reply("Your name is too long!")

        # Gets his old display_name
        old_display_name = session.scalars(select(Userbase.display_name).where(Userbase.user_id == ctx.author.id)).first()

        if old_display_name is None:
            await ctx.send("Please submit, and retry again!")

        else:
            # Detect illegal name change (2 identical names)
            if session.scalars(select(Userbase.display_name).where(Userbase.display_name == new_name)).first():
                return await ctx.reply("The name is already in use by another user.")

            stmt = update(Userbase).values(display_name=new_name).where(Userbase.user_id == ctx.author.id)
            session.execute(stmt)
            session.commit()

            await ctx.send(f"Name successfully set to **{new_name}**.")

            await rename_in_submission_list(self, old_display_name, new_name)



async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))

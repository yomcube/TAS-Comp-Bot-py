from discord.ext import commands
from api.db_classes import Userbase, get_session
from api.submissions import get_submission_channel, is_in_team
from sqlalchemy import select, update
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def rename_in_submission_list(self, ctx, old_display_name, new_display_name):
    submission_channel = await get_submission_channel(DEFAULT)
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

            if await is_in_team(ctx.author.id):
                for line in lines[1:]:
                    start_idx = line.find('(')
                    end_idx = line.find(')')
                    if start_idx != -1 and end_idx != -1:
                        within_parentheses = line[start_idx:end_idx]
                        if old_display_name in within_parentheses:
                            updated_within_parentheses = within_parentheses.replace(old_display_name, new_display_name)
                            line = line[:start_idx] + updated_within_parentheses + line[end_idx:]
                    new_lines.append(line)
            else:
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

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, *, new_name):

        if '@' in new_name:
            return await ctx.reply("You may not use @ in your name.")

        if len(new_name) > 120:
            return await ctx.reply("Your name is too long!")

        # Gets his old display_name
        async with get_session() as session:

            old_display_name = (
                await session.scalars(select(Userbase.display_name).where(Userbase.user_id == ctx.author.id))).first()

            if old_display_name is None:
                await ctx.send("Please submit, and retry again!")

            else:
                # Detect illegal name change (2 identical names)
                if (await session.scalars(select(Userbase.display_name).where(Userbase.display_name == new_name))).first():
                    return await ctx.reply("The name is already in use by another user.")

                stmt = update(Userbase).values(display_name=new_name).where(Userbase.user_id == ctx.author.id)
                await session.execute(stmt)
                await session.commit()

                await ctx.send(f"Name successfully set to **{new_name}**.")

                await rename_in_submission_list(self, ctx, old_display_name, new_name)


async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))

import discord
from discord.ext import commands
from api.db_classes import  Teams, get_session
from api.submissions import get_submission_channel, generate_submission_list
from api.utils import is_in_team
from sqlalchemy import select, update, or_
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


# async def rename_in_submission_list(self, old_display_name, new_display_name):
#     submission_channel = await get_submission_channel(DEFAULT)
#     channel = self.bot.get_channel(submission_channel)
#
#     async for message in channel.history(limit=3):
#         # Check if the message was sent by the bot
#         if message.author == self.bot.user:
#             lines = message.content.split('\n')
#             new_lines = [lines[0]]  # Preserve the first line as is ("Current submissions")
#
#             # Check if the new display name is already in use in the rest of the lines
#
#
#             for line in lines[1:]:
#                 start_idx = 3
#                 end_idx = line.find('(')
#                 if new_display_name in line[start_idx:end_idx]:
#                     return
#
#             for line in lines[1:]:
#                 start_idx = 3
#                 end_idx = line.find('(')
#                 before_parentheses = line[start_idx:end_idx]
#                 if old_display_name in before_parentheses:
#                     #updated_before_parentheses = before_parentheses.replace(old_display_name, new_display_name)
#                     line = line[:start_idx] + new_display_name + " " + line[end_idx:]
#                 new_lines.append(line)
#
#             new_content = '\n'.join(new_lines)
#             if new_content != message.content:
#                 await message.edit(content=new_content)
#             break  # Stop after finding the last bot message


class Setteamname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setteamname", description="Set your team's displayed name in the submission list",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, user: discord.Member, *, new_name: commands.clean_content):
        # ID of the person's team to be renamed
        user_id = user.id


        if '@' in new_name:
            return await ctx.reply("Illegal character found in team name")

        if len(new_name) > 120:
            return await ctx.reply("Your team name is too long!")

        if not await is_in_team(user_id):
            return await ctx.reply("That user is not in a team!")


        async with get_session() as session:

            # Detect illegal name change (2 identical names)
            if (await session.scalars(select(Teams.team_name).where(Teams.team_name == new_name))).first():
                return await ctx.reply("That team name is already in use.")

            # Update team name in db
            await session.execute(
                update(Teams)
                .where(
                    or_(Teams.leader == user_id, Teams.user2 == user_id, Teams.user3 == user_id,
                        Teams.user4 == user_id))
                .values(team_name=new_name)
            )

            await session.commit()

        # Update submission list
        await generate_submission_list(self)

        await ctx.send(f"Successfully set <@{user_id}>'s team name to **{new_name}**.")


async def setup(bot) -> None:
    await bot.add_cog(Setteamname(bot))

from discord.ext import commands
from api.db_classes import  Teams, get_session
from api.submissions import get_submission_channel
from api.utils import is_in_team
from sqlalchemy import select, update, or_
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


async def rename_in_submission_list(self, old_display_name, new_display_name):
    submission_channel = await get_submission_channel(DEFAULT)
    channel = self.bot.get_channel(submission_channel)

    async for message in channel.history(limit=3):
        # Check if the message was sent by the bot
        if message.author == self.bot.user:
            lines = message.content.split('\n')
            new_lines = [lines[0]]  # Preserve the first line as is ("Current submissions")

            # Check if the new display name is already in use in the rest of the lines


            for line in lines[1:]:
                start_idx = 3
                end_idx = line.find('(')
                if new_display_name in line[start_idx:end_idx]:
                    return

            for line in lines[1:]:
                start_idx = 3
                end_idx = line.find('(')
                before_parentheses = line[start_idx:end_idx]
                if old_display_name in before_parentheses:
                    #updated_before_parentheses = before_parentheses.replace(old_display_name, new_display_name)
                    line = line[:start_idx] + new_display_name + " " + line[end_idx:]
                new_lines.append(line)

            new_content = '\n'.join(new_lines)
            if new_content != message.content:
                await message.edit(content=new_content)
            break  # Stop after finding the last bot message


class Setteamname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setteamname", description="Set your team's displayed name in the submission list",
                             with_app_command=True)
    async def command(self, ctx, *, new_name):

        if '@' in new_name or '(' in new_name or ')' in new_name:
            return await ctx.reply("Illegal character(s) found in team name")

        if len(new_name) > 120:
            return await ctx.reply("Your team name is too long!")

        if not await is_in_team(ctx.author.id):
            return await ctx.reply("You are not in a team!")


        async with get_session() as session:

            # get old team name
            stmt = select(Teams.team_name).filter(
                (Teams.leader == ctx.author.id) | (Teams.user2 == ctx.author.id) | (Teams.user3 == ctx.author.id) |
                (Teams.user4 == ctx.author.id))

            result = await session.execute(stmt)
            old_team_name = result.scalars().first()

            # Detect illegal name change (2 identical names)
            if (await session.scalars(select(Teams.team_name).where(Teams.team_name == new_name))).first():
                return await ctx.reply("That team name is already in use.")

            await session.execute(
                update(Teams)
                .where(
                    or_(Teams.leader == ctx.author.id, Teams.user2 == ctx.author.id, Teams.user3 == ctx.author.id,
                        Teams.user4 == ctx.author.id))
                .values(team_name=new_name)
            )

            await session.commit()

            await ctx.send(f"Name successfully set team name to **{new_name}**.")

            await rename_in_submission_list(self, old_team_name, new_name)


async def setup(bot) -> None:
    await bot.add_cog(Setteamname(bot))

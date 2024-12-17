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



class Setteamname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setteamname", description="Set your team's displayed name in the submission list",
                             with_app_command=True)
    async def command(self, ctx, *, new_name):

        if '@' in new_name:
            return await ctx.reply("Illegal character found in team name")

        if len(new_name) > 120:
            return await ctx.reply("Your team name is too long!")

        if not await is_in_team(ctx.author.id):
            return await ctx.reply("You are not in a team")


        async with get_session() as session:

            # Detect illegal name change (2 identical names)
            if (await session.scalars(select(Teams.team_name).where(Teams.team_name == new_name))).first():
                return await ctx.reply("That team name is already in use.")

            # Update team name in db
            await session.execute(
                update(Teams)
                .where(
                    or_(Teams.leader == ctx.author.id, Teams.user2 == ctx.author.id, Teams.user3 == ctx.author.id,
                        Teams.user4 == ctx.author.id))
                .values(team_name=new_name)
            )

            await session.commit()

        # Update submission list
        await generate_submission_list(self)

        await ctx.send(f"Successfully set team name to **{new_name}**.")


async def setup(bot) -> None:
    await bot.add_cog(Setteamname(bot))

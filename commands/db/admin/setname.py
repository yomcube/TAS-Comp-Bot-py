import discord
from discord.ext import commands
from api.db_classes import Userbase, get_session
from api.submissions import get_submission_channel, generate_submission_list
from sqlalchemy import select, update
import os
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')



class Setname(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="setname", description="Set your displayed name in the submission list",
                             with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, user: discord.Member, *, new_name: commands.clean_content):

        if '@' in new_name:
            return await ctx.reply("You may not use @ in your name.")

        if len(new_name) > 120:
            return await ctx.reply("Your name is too long!")

        # Gets his old display_name
        async with get_session() as session:

            user_id = user.id

            old_display_name = (
                await session.scalars(select(Userbase.display_name).where(Userbase.user_id == user_id))).first()

            if old_display_name is None:
                return await ctx.send("This person has never submitted. Please submit first!")

            else:
                # Detect illegal name change (2 identical names)
                if (await session.scalars(select(Userbase.display_name).where(Userbase.display_name == new_name))).first():
                    return await ctx.reply("The name is already in use by another user.")

                # Update name in database
                stmt = update(Userbase).values(display_name=new_name).where(Userbase.user_id == user_id)
                await session.execute(stmt)
                await session.commit()

        # Update submission list
        await generate_submission_list(self)

        await ctx.send(f"Sucessfully set <@{user_id}>'s name to **{new_name}**.")


async def setup(bot) -> None:
    await bot.add_cog(Setname(bot))

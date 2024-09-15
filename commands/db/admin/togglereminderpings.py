import os
import discord
from discord.ext import commands
from api.db_classes import get_session, ReminderPings
from sqlalchemy import select, insert, update
from dotenv import load_dotenv

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Togglereminderpings(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="toggle-reminder-pings", aliases=['trp'],
                             description="Toggle on/off everyone reminder pings in speed tasks", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def command(self, ctx, comp: str = DEFAULT):

        # TODO: detect which server you are in, so the comp argument is no longer needed
        async with get_session() as session:
            query = select(ReminderPings.ping).where(ReminderPings.guild_id == ctx.guild.id)
            result = (await session.execute(query)).first()

            if result[0] is None:
                stmt = insert(ReminderPings).values(ping=0, guild_id=ctx.message.guild.id, comp=comp)
                await session.execute(stmt)
                new_setting = False


            elif result[0] == 0:
                stmt = update(ReminderPings).values(ping=1, guild_id=ctx.message.guild.id, comp=comp)
                await session.execute(stmt)
                new_setting = True

            else:
                stmt = update(ReminderPings).values(ping=0, guild_id=ctx.message.guild.id, comp=comp)
                await session.execute(stmt)
                new_setting = False

            await session.commit()

        await ctx.send(f"The speed task reminders pings have been set to {new_setting}!")


async def setup(bot) -> None:
    await bot.add_cog(Togglereminderpings(bot))

import os
import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from api.db_classes import get_session, SpeedTaskLength, SpeedTaskReminders
from api.utils import has_host_role
from sqlalchemy import select, insert, update
from sqlalchemy.exc import NoResultFound
from dotenv import load_dotenv
from typing import List

load_dotenv()
DEFAULT = os.getenv('DEFAULT')  # Choices: mkw, sm64


class Speedtaskreminder(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="speed-task-reminders", aliases=['str'],
                             description="Set the reminders necessary for speed tasks", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, reminders: Greedy[int]):
        if len(reminders) > 4:
            await ctx.send("You can't set more than 4 reminders.")
            return

        async with get_session() as session:
            # Prepare the reminders, filling with None if fewer than 4
            reminders_filled = reminders + [None] * (4 - len(reminders))

            comp_name = DEFAULT
            guild_id = ctx.guild.id

            stmt = select(SpeedTaskReminders).where(SpeedTaskReminders.guild_id == guild_id)
            result = await session.execute(stmt)
            existing_reminder = result.scalar_one_or_none()

            if existing_reminder:
                # Update the existing row
                existing_reminder.comp = comp_name
                existing_reminder.reminder1 = reminders_filled[0]
                existing_reminder.reminder2 = reminders_filled[1]
                existing_reminder.reminder3 = reminders_filled[2]
                existing_reminder.reminder4 = reminders_filled[3]
            else:
                # If no existing row is found, create a new one
                new_task_reminder = SpeedTaskReminders(
                    comp=comp_name,
                    reminder1=reminders_filled[0],
                    reminder2=reminders_filled[1],
                    reminder3=reminders_filled[2],
                    reminder4=reminders_filled[3],
                    guild_id=guild_id
                )
                session.add(new_task_reminder)

            # Commit changes to the database
            await session.commit()

        # Confirmation message
        await ctx.send(
            f"Reminders set: {', '.join(str(r) for r in reminders if r is not None)} minutes before the deadline.")


async def setup(bot) -> None:
    await bot.add_cog(Speedtaskreminder(bot))

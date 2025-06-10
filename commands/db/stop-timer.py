import discord
import shared
from discord.ext import commands
import os
from dotenv import load_dotenv
from sqlalchemy import update, select

from api.db_classes import SpeedTask, get_session, Submissions
from api.submissions import first_time_submission
from api.utils import is_task_currently_running, get_host_role, get_submitter_role
from commands.db.requesttask import has_requested_already, is_time_over

load_dotenv()
DEFAULT = os.getenv('DEFAULT')


class ConfirmView(discord.ui.View):
    def __init__(self, author: discord.User, timeout=60):
        super().__init__(timeout=timeout)
        self.author = author
        self.value = None

    async def disable_all_buttons(self):
        for child in self.children:
            if isinstance(child, discord.ui.Button):
                child.disabled = True

    async def interaction_check(self, interaction: discord.Interaction) -> bool:
        if interaction.user != self.author:
            await interaction.response.send_message("You're not allowed to interact with this.", ephemeral=True)
            return False
        return True

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green)
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = True
        await self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel(self, interaction: discord.Interaction, button: discord.ui.Button):
        self.value = False
        await self.disable_all_buttons()
        await interaction.response.edit_message(view=self)
        self.stop()


class StopTimer(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.command(name="stop-timer", aliases=['end-timer'])
    async def command(self, ctx, user: discord.Member = None):
        current_task = await is_task_currently_running()

        is_speed_task = current_task[4]
        is_task_released = current_task[7]
        command_author = ctx.author

        # Check if a speed task is ongoing
        if not is_speed_task:
            return await ctx.send("There is no active speed task.")

        # If no user is specified, then it is implied you are ending the speed task for yourself
        if user is None:
            if ctx.guild is not None:
                return await ctx.send("Please use this in DMs!")
            competitor = ctx.author.id
        else:
            # Check host permission
            if ctx.guild is None:
                return await ctx.send("This can only be used in a server by a host.")

            role_id = await get_host_role(ctx.guild.id)
            has_role = discord.utils.get(ctx.author.roles, id=role_id) is not None

            if not has_role:
                return await ctx.send("Only a host can end someone else's timer early.")

            competitor = user.id

        # Check if they have a task running, and the task isn't publicly released
        if not await has_requested_already(competitor) and not is_task_released:

            # Custom message
            if user is None:
                return await ctx.send("You have not requested the speed task!")
            else:
                return await ctx.send("This competitor has not requested the speed task!")

        # Check if they have requested, but their time ended already
        if await is_time_over(competitor):
            return await ctx.send("Task is already over!")

        # Ask command author for confirmation
        view = ConfirmView(author=command_author)
        await ctx.send("Are you sure you want to end the task early? There is no going back.", view=view)
        await view.wait()

        if view.value is None:
            await ctx.send("Request timed out. The task is still ongoing.")
            cancelling = False
        elif view.value:
            await ctx.send("The task has been ended early successfully.")
            cancelling = True
        else:
            await ctx.send("Your cancelled the request. The task is still ongoing.")
            cancelling = False

        # Cancel the person's task
        if cancelling:
            async with get_session() as session:
                stmt = (
                    update(SpeedTask)
                    .where(SpeedTask.user_id == competitor)
                    .values(active=0)
                )

                await session.execute(stmt)
                await session.commit()

            # If we're cancelling someone else's task, DM them.
            if competitor != command_author.id:
                await self.bot.get_user(competitor).send(f"Your timer has been ended early by <@{command_author.id}>. Thank you for competing!")

            # Check if competitor has submitted. If yes, give him is submitted role
            async with get_session() as session:
                query = select(Submissions.user_id).where(Submissions.user_id == competitor)
                result = (await session.execute(query)).first()

            if result:
                # Give competitor his submitted role
                guild_id = shared.main_guild.id

                if guild_id is None:
                    print("Guild not detected yet.")
                    return

                submitter_role = await get_submitter_role(DEFAULT)

                # Fetch the member from the detected guild
                server = self.bot.get_guild(guild_id)
                member = server.get_member(competitor)

                if member:
                    role = server.get_role(submitter_role)
                    if role:
                        if role not in member.roles:
                            await member.add_roles(role)
                            print(f"Role {role.name} has been assigned to {member.display_name}.")
                    else:
                        print(f"Role with ID {submitter_role} not found in this server.")
                else:
                    print(f"User with ID {competitor} not found in this server.")



async def setup(bot) -> None:
    await bot.add_cog(StopTimer(bot))

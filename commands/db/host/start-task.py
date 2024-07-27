from discord.ext import commands
import discord
import os
from dotenv import load_dotenv
from datetime import date
from api.utils import is_task_currently_running, has_host_role, get_team_size
from api.submissions import get_submission_channel, get_seeking_channel
from api.db_classes import Tasks, Submissions, Teams, get_session
from sqlalchemy import insert, delete, select

load_dotenv()
DEFAULT = os.getenv('DEFAULT')

class TeamsView(discord.ui.View):
    def __init__(self, bot, final_message):
        super().__init__()
        self.bot = bot
        self.final_message = final_message
        self.partners = []  # list to store users who have pressed the button

    @discord.ui.button(label="🤝", style=discord.ButtonStyle.blurple)
    async def free(self, interaction: discord.Interaction, button: discord.ui.Button):
        username = interaction.user.name
        if username in self.partners:
            self.partners.remove(username)
            await interaction.response.send_message("You have been removed from the list of available partners.", ephemeral=True)
        else:
            self.partners.append(username)
            await interaction.response.send_message("You have been added to the list of available partners!\nClick again to remove yourself, or else it will remove you by default when you find a team.", ephemeral=True)

        await self.update_message()

    async def update_message(self):
        teams_content = "__**Confirmed teams:**__\n"
        partners_content = "__**Available partners:**__\n"

        try:
            # Retrieve teams from db
            async with get_session() as session:
                result = await session.execute(select(Teams))
                rows = result.scalars().all()

            # Write each line of teams
            teams = {}
            for row in rows:
                row_data = []
                for column in row.__table__.columns:
                    # value is discord account id
                    value = getattr(row, column.name)

                    if value is not None and column.name != "index":
                        display_name = self.bot.get_user(value).display_name
                        row_data.append(display_name)
                teams[row.index] = row_data
                teams_content += f"{row.index}. {', '.join(row_data)} \n"
            
            # Write each line of partners
            for partner in self.partners:
                if partner in teams:
                    self.partners.pop(partner)
                else:
                    partners_content += f"{partner}\n"
            
            await self.final_message.edit(content=f"{teams_content}\n{partners_content}")
        
        except AttributeError as e:
            print(f"AttributeError: {e}")

class Start(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="start-task", description="Start a task", with_app_command=True)
    @has_host_role()
    async def command(self, ctx, number: int, team_size: int = 1, multiple_tracks: int = 0,
                      speed_task: int = 0, year: int = None):

        if not year:
            year = date.today().year

        if await is_task_currently_running() is None:
            async with get_session() as session:
                # Mark task as ongoing
                await session.execute(insert(Tasks).values(task=number, year=year, is_active=1, team_size=team_size,
                                                           multiple_tracks=multiple_tracks, speed_task=speed_task))

                # Clear submissions from previous task, as well as potential teams
                await session.execute(delete(Submissions))
                await session.execute(delete(Teams))
                # Commit changes to both tables affected
                await session.commit()

            # Delete previous "Current submissions" message in submission channel
            channel_id = await get_submission_channel(DEFAULT)
            channel = self.bot.get_channel(channel_id)

            try:
                async for message in channel.history(limit=5):  # Adjust limit as necessary
                    if message.author == self.bot.user:
                        await message.delete()
                        break

            except AttributeError:
                await ctx.send(
                    "Please set the submission channel with `/set-submission-channel`! (Ask an admin if you do not have permission)")

            await ctx.send(f"Successfully started **Task {number} - {year}**!")

        else:
            # if a task is already ongoing...
            await ctx.send(f"A task is already ongoing.\nPlease use `/end-task` to end the current task.")
            return
        
        
        
        ######################
        #### TEAMS SYSTEM ####
        ######################
        
        seeking_channel_id = await get_seeking_channel(DEFAULT)
        seeking_channel = self.bot.get_channel(seeking_channel_id)
        
        if seeking_channel is None:
            await ctx.send("Seeking channel not found. Please set the seeking channel with `/set-seeking-channel`! (Ask an admin if you do not have permission)")
            return

        ctx.author
        team_size = await get_team_size()

        # Verify if it's indeed a collab task
        if team_size < 2:
            return

        teams_content = "__**Confirmed teams:**__\n"
        partners_content = "__**Available partners:**__\n"

        try:
            # Retrieve teams from db
            async with get_session() as session:
                result = await session.execute(select(Teams))
                rows = result.scalars().all()

            # Write each line of teams
            teams = {}
            for row in rows:
                row_data = []
                for column in row.__table__.columns:
                    # value is discord account id
                    value = getattr(row, column.name)

                    if value is not None and column.name != "index":
                        display_name = self.bot.get_user(value).display_name
                        row_data.append(display_name)
                teams[row.index] = row_data
                teams_content += f"{row.index}. {', '.join(row_data)} \n"
            
            # Write each line of partners
            partners = []
            partners_content = "__**Available partners:**__\n"
            for partner in partners:
                if partner in teams:
                    partners.pop(partner)
                else:
                    partners_content += f"{partner}\n"

            final_message = await seeking_channel.send(f"{teams_content}\n{partners_content}")
            await final_message.pin()

            teams_view = TeamsView(self.bot, final_message)

            await final_message.edit(view=teams_view)
        
        except AttributeError:
            await ctx.send(f"Please set the seeking channel with `/set-seeking-channel`! (Ask an admin if you do not have permission)")

async def setup(bot) -> None:
    await bot.add_cog(Start(bot))

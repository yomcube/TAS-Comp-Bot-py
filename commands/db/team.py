import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from api.utils import get_team_size
from api.db_classes import Teams, get_session
from sqlalchemy import select, insert, update, delete, inspect, or_


class AcceptDeclineButtons(discord.ui.View):
    def __init__(self, user: discord.Member, callback):
        super().__init__(timeout=60)  # Timeout after 60 seconds
        self.user = user
        self.callback = callback
        self.value = None
        self.handled = False

    @discord.ui.button(label="Accept", style=discord.ButtonStyle.green)
    async def accept(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = True
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has accepted the collaboration!",
                                                view=self)
        await self.callback(self.user, True)

    @discord.ui.button(label="Decline", style=discord.ButtonStyle.red)
    async def decline(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user != self.user:
            await interaction.response.send_message("You cannot click this button!", ephemeral=True)
            return
        self.value = False
        self.disable_all_buttons()
        await interaction.response.edit_message(content=f"{self.user.mention} has declined the collaboration!",
                                                view=self)
        await self.callback(self.user, False)

    async def on_timeout(self):
        if not self.handled:
            self.disable_all_buttons()
            await self.message.edit(view=self)
            await self.callback(self.user, False)

    def disable_all_buttons(self):
        for item in self.children:
            item.disabled = True
        self.handled = True


class Team(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_users = {}
        self.ctx = None
        self.author = None
        self.team_size = None

    @commands.hybrid_command(name="collab", aliases=["team"],
                             description="Collaborate with someone during a team task", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def collab(self, ctx, users: Greedy[discord.Member]):
        self.ctx = ctx
        self.author = ctx.author
        self.team_size = await get_team_size()

        #####################
        # Case handling
        #####################

        # Is there a task running?
        if self.team_size is None:
            return await ctx.send("There is no task running currently.")

        # Verify if it's indeed a collab task
        elif self.team_size < 2:
            return await ctx.send("This is a solo task. You may **not** collaborate!")


        # Make sure they don't try to collab with too many people
        elif len(users) + 1 > self.team_size:
            return await ctx.send("You are trying to collab with too many people!")

        # Make sure they are not already in a team
        async with get_session() as session:
            inspector = inspect(Teams)
            columns = inspector.columns
            conditions = [getattr(Teams, column.name) == ctx.author.id for column in columns if
                          column.type.python_type == int]
            stmt = select(Teams).filter(or_(*conditions))
            result = await session.execute(stmt)
            results = result.scalars().all()
            if results:
                return await ctx.send("You are already in a team.")

        # Make sure they are not collaborating with themselves: absurd
        for user in users:
            if user.id == self.author.id:
                return await ctx.send("Collaborating with...yourself? sus")

        #####################
        # Button view
        #####################

        self.pending_users = {user.id: None for user in users}

        for user in users:
            view = AcceptDeclineButtons(user, self.user_response)
            message = await ctx.send(
                f"{user.mention}, {ctx.author.display_name} wants you to collaborate with them. Do you accept?",
                view=view)
            view.message = message  # Store the message in the view for later editing

    async def user_response(self, user, accepted):
        self.pending_users[user.id] = accepted
        if all(response is not None for response in self.pending_users.values()):
            if all(self.pending_users.values()):

                # Everyone has accepted
                user_mentions = ", ".join(f"<@{user_id}>" for user_id in self.pending_users)
                await self.ctx.send(f"{self.author.mention} is collaborating with {user_mentions}!")

                # Add team to db
                user_ids = list(self.pending_users.keys())
                async with get_session() as session:
                    await session.execute(
                        insert(Teams).values(leader=self.author.id, user2=user_ids[0] if len(user_ids) > 0 else None,
                                             user3=user_ids[1] if len(user_ids) > 1 else None,
                                             user4=user_ids[2] if len(user_ids) > 2 else None))

                    await session.commit()

                # clear pending users list
                self.pending_users.clear()
            else:
                await self.ctx.send("One or more users declined the collaboration. No teams have been formed.")
                self.pending_users.clear()

    @commands.hybrid_command(name="dissolve", aliases=["disband"],
                                 description="Dissolve your team (WARNING: No confirmation)", with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def dissolve(self, ctx):
        async with get_session() as session:
            # Check if the user is the leader of any team
            stmt = select(Teams).where(Teams.leader == ctx.author.id)
            result = await session.execute(stmt)
            team = result.scalar()

            if team:
                # Delete the team
                await session.execute(delete(Teams).where(Teams.leader == ctx.author.id))
                await session.commit()
                await ctx.send("Your team has been dissolved.")
            else:
                await ctx.send("You are not the leader of any team.")




async def setup(bot):
    await bot.add_cog(Team(bot))

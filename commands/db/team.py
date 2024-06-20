import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from api.utils import get_team_size
from api.mkwii.mkwii_utils import characters, vehicles
from api.db_classes import Submissions, get_session
from sqlalchemy import select


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
    async def collab(self, ctx, users: Greedy[discord.Member]):
        self.ctx = ctx
        self.author = ctx.author
        self.team_size = await get_team_size()

        #####################
        # Case handling
        #####################

        # Verify if it's indeed a collab task
        if self.team_size < 2:
            return await ctx.send("This is a solo task. You may **not** collaborate!")

        # Is there a task running?
        elif self.team_size is None:
            return await ctx.send("There is no task running currently.")

        # Make sure doesn't try to collab with too many people
        elif len(users) + 1 > self.team_size:
            return await ctx.send("You are trying to collab with too many people!")

        # Make sure he is not collaborating with himself: absurd
        for user in users:
            if user.id == self.author.id:
                return await ctx.send("Collaborating with...yourself? sus")

        #####################
        # Logic
        #####################

        self.pending_users = {user.id: None for user in users}

        for user in users:
            view = AcceptDeclineButtons(user, self.user_response)
            message = await ctx.send(f"{user.mention}, do you want to join the collaboration?", view=view)
            view.message = message  # Store the message in the view for later editing

    async def user_response(self, user, accepted):
        self.pending_users[user.id] = accepted
        if all(response is not None for response in self.pending_users.values()):
            if all(self.pending_users.values()):
                user_mentions = ", ".join(f"<@{user_id}>" for user_id in self.pending_users)
                await self.ctx.send(f"{self.author.mention} is collaborating with {user_mentions}!")
            else:
                await self.ctx.send("One or more users declined the collaboration.")


async def setup(bot):
    await bot.add_cog(Team(bot))

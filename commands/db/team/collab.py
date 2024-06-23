import discord
from discord.ext import commands
from discord.ext.commands import Greedy
from api.utils import get_team_size, is_in_team
from api.db_classes import Teams, Userbase, get_session
from api.submissions import new_competitor
from sqlalchemy import select, insert, update, delete


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


class Collab(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.pending_users = {}
        self.ctx = None
        self.author = None
        self.team_size = None

    @commands.hybrid_command(name="collab", description="Collaborate with someone during a team task", with_app_command=True)
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
        if await is_in_team(ctx.author.id):
            return await ctx.send("You are already in a team.")

        # Make sure they are not collaborating with themselves: absurd
        for user in users:
            if user.id == self.author.id:
                return await ctx.send("Collaborating with... yourself? sus")

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

                # Add team to Teams db
                user_ids = list(self.pending_users.keys())
                async with get_session() as session:
                    await session.execute(
                        insert(Teams).values(leader=self.author.id, user2=user_ids[0] if len(user_ids) > 0 else None,
                                             user3=user_ids[1] if len(user_ids) > 1 else None,
                                             user4=user_ids[2] if len(user_ids) > 2 else None))

                    # Add any new users to Userbase db
                    for id in self.pending_users:
                        if await new_competitor(id):
                            # adding him to the user database.
                            await session.execute(insert(Userbase).values(user_id=id, user=self.bot.get_user(id).name,
                                                                              display_name=self.bot.get_user(id).display_name))
                    # Commit both changes
                    await session.commit()

                # clear pending users list
                self.pending_users.clear()
            else:
                await self.ctx.send("One or more users declined the collaboration. No teams have been formed.")
                self.pending_users.clear()
                

async def setup(bot):
    await bot.add_cog(Collab(bot))
from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, category: str = ""):
        if category == "":

            help_menu = """**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95 and shxd
List of commands\n
**Commands**:
  **help** -- this
  **fun** -- Fun commands, such as slots
  **misc** -- Miscellaneous commands
  **host** -- Host-only commands, for handling tasks.
  **admin** -- Other admin commands
      
Write `$help <category>` to view help for a specific category.
Note: Most commands are available using the prefix, aswell as using `/`.
    """

        elif category == "fun":

            help_menu = """**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95 and shxd
Fun commands 👀\n
**Commands**:
  **balance** -- Prints your balance
  **coinflip** -- Bet on a coinflip against the bot, or another player. For now, only betting 5 coins is possible.
  **connect4** -- Play connect 4 against MKWTASCompBot in any of 3 modes: easy, normal and hard, or against another player.
  **rps** -- Play rock paper scissors against the bot, or against another player. Coins are involved.
  **slots** -- Play the famous slot machine. Default number of emotes is 3. Coins are involved.
"""

        elif category == "misc":
            help_menu = """**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95 and shxd
Miscellaenous commands\n
  **info** -- Shows information about the status of your submission. (DM only)
  **setname** -- Changes your display name for the submission channel (Not your server name!)
  **tracks** -- Picks a random track from the game!
  **urban** -- Search urban dictionary for a word or expression!
  **weather** -- Get the weather of a city!
"""

        elif category == "host":
            help_menu = """**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95 and shxd
Host commands :mishchievous:\n
  **/dm** -- Make the bot dm someone!
  **/edit-submission** -- Edits someone's submission status: time, dq (True/False), dq reason
  **end-task** -- Ends the current task (No confirmation)
  **get-results** -- Prints the results of the current (ended or not) task. Valid and DQ'ed runs
  **get-submissions** -- Your bread and butter for starting to judge and time runs!
  **/start-task** -- Starts a new task. Warning: this deletes last task's stored submissions, results, and 'Current submission' message.
  **/submit** -- Submit a file for someone, should an issue arise.
"""

        elif category == "admin":
            help_menu = """**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95 and shxd
Admin commands :cereal:\n
  **addcoins** -- Adds coins to someone's balance
  **say** -- Make the bot say something in a channel!
  **set-host-role -- Sets the host role that can use all the Host commands. Default role is a role called 'Host'. 
  **set-submission-channel** -- Set the submission channel where the 'Current submissions' message is.
  """




        await ctx.send(help_menu)





async def setup(bot):
    await bot.add_cog(Help(bot))


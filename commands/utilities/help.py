from discord.ext import commands

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="help", description="List of commands", with_app_command=True)
    async def help(self, ctx, category: str = ""):
        try:
            if category == "":

                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    List of commands\n
    **Commands**:
      **help** -- this
      **comp** -- Public competition-related commands
      **misc** -- Miscellaneous commands
      **fun** -- Fun commands, such as slots
      **host** -- Host-only commands, for handling tasks.
      **admin** -- Admin commands
      **credits** -- View more info about the bot and its creators
          
    Write `$help <category>` to view help for a specific category. (Except credits, it has its standalone command.)
    Note: Most commands are available using the prefix `$`, aswell as using `/`.
        """

            if category.lower() == "comp":
                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    Competition commands\n
      **collab** -- Team up with someone during a collab task!
      **info** -- Shows information about the status of your submission. (DM only)
      **leaveteam** -- Leave your team during a collab task.
      **requesttask** -- Request the task (sent to your DMs) during a speed task.
      **setteamname** -- Changes your team's name in the submission channel. Only during collab tasks.
      **task-info** -- View information about the current task, such as deadline and host.
      **teams** -- View the list of teams during a collab task.
    """


            elif category.lower() == "fun":

                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    Fun commands 👀\n
    **Commands**:
      **8ball** -- Have a question? Ask the bot for his wisdom! Only 'yes/no' and 'when' questions are supported. 
      **balance** -- Prints your balance
      **balancetop** -- View the balance leaderboard for this server.
      **coinflip** -- Bet on a coinflip against the bot, or another player. For now, only betting 5 coins is possible.
      **connect4** -- Play connect 4 against MKWTASCompBot in any of 3 modes: easy, normal and hard, or against another player.
      **joke** -- Get a good ol' joke from the bot!
      **memory** -- Play a memory game! Default board size is 4x4. Be warned: board size 6 and up are way harder due to emoji size.
      **rps** -- Play rock paper scissors against the bot, or against another player. Coins are involved.
      **slots** -- Play the famous slot machine. Default number of emotes is 3. Coins are involved.
    """

            elif category.lower() == "misc":
                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    Miscellaneous commands\n
      **quote** -- Read an inspirational quote!
      **tracks** -- Picks a random track from the game!
      **urban** -- Search urban dictionary for a word or expression!
      **weather** -- Get the weather of a city!
    """


            elif category.lower() == "host":
                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    Host commands :P\n
      **delete-submission** -- Delete someone's submission. 
      **/dm** -- Make the bot dm someone!
      **/edit-submission** -- Edits someone's submission status: time, dq (True/False), dq reason
      **end-task** -- Ends the current task (Warning: No confirmation). This does not clear submissions.
      **get-results** -- Prints the results of the current (ended or not) task. Valid and DQ'ed runs
      **get-submissions** -- Your bread and butter for starting to judge and time runs!
      **hostdissolve** -- Dissolve a team. Use $teams to see different team indexes.
      **set-deadline** -- Change the deadline. Time in UNIX!
      **speed-task-desc** -- Set the description of a speed task.
      **speed-task-length** -- Set the duration competitors have to submit to a speed task.
      **speed-task-reminders** -- Set the reminders for a speed task. Up to 4 reminders.
      **/start-task** -- Starts a new task. Warning: this deletes last task's stored submissions, results, and 'Current submission' message.
      **/submit** -- Submit a file for someone.
    """

            elif category.lower() == "admin":
                help_menu = """**MKWTASCompBot** - A Multi TAS Comp Bot
    Admin commands \n
      **addcoins** -- Adds coins to someone's balance (or remove, if a negative number is specified).
      **config** -- Configure the different roles and channels
      **say** -- Make the bot say something in a channel!
      **set-announcement-role** -- Set the announcement channel.
      **set-host-role** -- Sets the host role that can use all the Host commands. Default role is a role called 'Host'.
      **set-logs-channel** -- Sets the dm logging channel 
      **set-seeking-channel** -- Sets the Seeking partners channel
      **set-submission-channel** -- Set the submission channel where the 'Current submissions' message is.
      **set-submitter-role** -- Set the submitter role. Given out when user submit.
      **set-tasks-channel** -- Set the tasks channel.
      **setname** -- Change someone's name for the submission channel.
      **toggle-reminder-pings** -- Toggle whether we want to ping @ everyone when doing speed task reminders. Default: False
      """


            await ctx.send(help_menu)


        except UnboundLocalError:
            await ctx.send("Invalid argument.")






async def setup(bot):
    await bot.add_cog(Help(bot))


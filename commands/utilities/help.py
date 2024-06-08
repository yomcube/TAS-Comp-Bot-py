from discord.ext import commands

AUTHOR_LINE = "**MKWTASCompBot** - Comp bot by Crackhex, DashQC, Epik95, shxd and Aurumaker72"

class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx, category: str = ""):
        if category == "":

            help_menu = f"""{AUTHOR_LINE}
List of commands\n
**Commands**:
  **help** -- this
  **fun** -- Fun commands, such as slots
  **util** -- Utility commands
  **misc** -- Miscellaneous commands
  **voice** -- Voice chat commands
  **host** -- Host-only commands, for handling tasks.
  **admin** -- Admin commands
      
Write `$help <category>` to view help for a specific category.
Note: Most commands are available using the prefix `$`, aswell as using `/`.
    """

        elif category == "fun":

            help_menu = f"""{AUTHOR_LINE}
Fun commands 👀\n
**Commands**:
  **8ball** -- Have a question? Ask the bot for his wisdom! Only 'yes/no' and 'when' questions are supported. 
  **balance** -- Prints your balance
  **balancetop** -- View the balance leaderboard for this server.
  **coinflip** -- Bet on a coinflip against the bot, or another player. For now, only betting 5 coins is possible.
  **connect4** -- Play connect 4 against MKWTASCompBot in any of 3 modes: easy, normal and hard, or against another player.
  **joke** -- Get a good ol' joke from the bot!
  **rps** -- Play rock paper scissors against the bot, or against another player. Coins are involved.
  **slots** -- Play the famous slot machine. Default number of emotes is 3. Coins are involved.
"""

        elif category == "util":
                    help_menu = f"""{AUTHOR_LINE}
Utility commands\n
  **encode** -- Encodes a Mupen64 movie into an mp4
"""

        elif category == "misc":
            help_menu = f"""{AUTHOR_LINE}
Miscellaneous commands\n
  **info** -- Shows information about the status of your submission. (DM only)
  **setname** -- Changes your display name for the submission channel (Not your server name!)
  **tracks** -- Picks a random track from the game!
  **urban** -- Search urban dictionary for a word or expression!
  **weather** -- Get the weather of a city!
"""

        elif category == "voice":
            help_menu = f"""{AUTHOR_LINE}
Voice chat commands :musical_note: \n
  **joinvc** -- Invites the bot in your vc.
  **leave** -- Kicks the bot off of your vc.
  **play** -- Plays a youtube video (sound-only) inside the vc!
  **stop** -- Stops the ongoing video.
"""




        elif category == "host":
            help_menu = f"""{AUTHOR_LINE}
Host commands :mishchievous:\n
  **/dm** -- Make the bot dm someone!
  **/edit-submission** -- Edits someone's submission status: time, dq (True/False), dq reason
  **end-task** -- Ends the current task (Warning: No confirmation). This does not clear submissions.
  **get-results** -- Prints the results of the current (ended or not) task. Valid and DQ'ed runs
  **get-submissions** -- Your bread and butter for starting to judge and time runs!
  **/start-task** -- Starts a new task. Warning: this deletes last task's stored submissions, results, and 'Current submission' message.
  **/submit** -- Submit a file for someone, should an issue arise. Use this as last resort :P
"""

        elif category == "admin":
            help_menu = f"""{AUTHOR_LINE}
Admin commands :cereal:\n
  **addcoins** -- Adds coins to someone's balance (or remove, if a negative number is specified).
  **say** -- Make the bot say something in a channel!
  **set-host-role -- Sets the host role that can use all the Host commands. Default role is a role called 'Host'. 
  **set-submission-channel** -- Set the submission channel where the 'Current submissions' message is.
  """

        await ctx.send(help_menu)





async def setup(bot):
    await bot.add_cog(Help(bot))


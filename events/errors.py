import sys
import traceback

from discord.ext import commands


class Errors(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    # Maybe there's a better way to do this, but this is error handling
    async def on_command_error(self, ctx, error):
        if hasattr(ctx.command, 'on_error'):
            return
        ignored = ()
        error = getattr(error, 'original', error)
        msg = None
        match error:
            case _ if isinstance(error, ignored):
                return

            case _ if isinstance(error, commands.MissingPermissions):
                print("missing perms\n")
                msg = f'You lack permissions to execute `{self.bot.command_prefix}{ctx.command}`.'

            case _ if isinstance(error, commands.NotOwner):
                print("not owner\n")
                msg = f'Only the bot owner has permission to execute `{ctx.command}`.'

            case _ if isinstance(error, commands.CommandNotFound):
                # separate out everything before the first occurrence of a space, which is the command itself
                msg = "That is not a valid command."

            case _ if isinstance(error, commands.MemberNotFound):
                msg = "The member specified does not exist."

            case _ if isinstance(error, commands.MissingRequiredArgument):
                msg = f'Missing arguments in {ctx.command}.'

            # Use checks to verify for permissions (if someone has the correct role for X command)
            case _ if isinstance(error, commands.CheckFailure):
                msg = "You may not use this command!"

            case _ if isinstance(error, commands.PrivateMessageOnly):
                msg = "This command is only usable in DMs with the bot."

        if msg:
            return await ctx.send(msg)

        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


async def setup(bot):
    await bot.add_cog(Errors(bot))

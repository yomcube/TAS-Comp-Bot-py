from discord.ext import commands
import sys
import traceback

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
        if isinstance(error, ignored):
            return
        elif isinstance(error, commands.MissingPermissions):
            print("missing perms\n")
            return await ctx.send(f'You lack permissions to execute `{self.bot.command_prefix}{ctx.command}`.')
        elif isinstance(error, commands.NotOwner):
            print("not owner\n")
            return await ctx.send(f'Only the bot owner has permission to execute `{ctx.command}`.')
        elif isinstance(error, commands.CommandNotFound):
            return await ctx.send(f"{ctx.command} is not a valid command.")
        elif isinstance(error, commands.MemberNotFound):
            return await ctx.send("The member specified does not exist.")
        elif isinstance(error, commands.MissingRequiredArgument):
            return await ctx.send(f'Missing arguments in {ctx.command}.')
        elif isinstance(error, commands.CheckFailure): # I use checks to verify for permissions (if someone has the correct role for X command)
            return await ctx.send("You may not use this command!")
        elif isinstance(error, commands.PrivateMessageOnly):
            return await ctx.send("This command is only usable in DMs with the bot.")
        print(f'Ignoring exception in command {ctx.command}:', file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

async def setup(bot):
    await bot.add_cog(Errors(bot))

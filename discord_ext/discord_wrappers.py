from api.errors import AppError


def command_handler():
    def decorator(func):
        async def wrapper(self, ctx, *args, **kwargs):
            try:
                return await func(self, ctx, *args, **kwargs)

            except AppError as e:
                # All known user errors land here
                await ctx.send(str(e), ephemeral=True)

            except Exception as e:
                # All unexpected errors land here
                print("Unexpected error:", e)
                await ctx.send("An unexpected error occurred.")

        return wrapper
    return decorator


import random

from discord.ext import commands

from api.utils import get_balance, calculate_winnings, add_balance, deduct_balance


class Slots(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="slots", description="Slots through server emojis", with_app_command=True)
    async def command(self, ctx, number: int = 3):
        if number > 20:
            return await ctx.send(f"Please use a smaller number! It's not like you would win slots {number} anyway...")

        user_id = ctx.author.id
        guild_id = ctx.message.guild.id
        cost_per_play = 5
        user_balance = await get_balance(user_id, guild_id)
        if user_balance < cost_per_play:
            await ctx.reply("You don't have enough coins to play.")
            return

        await deduct_balance(user_id, guild_id, cost_per_play)
        user_balance = user_balance - cost_per_play

        emojis = ctx.message.guild.emojis
        emojis_list = [str(emoji) for emoji in emojis]
        random_emojis = random.choices(emojis_list, k=number)
        result = " ".join(random_emojis)
        play_again_text = f"{user_balance} coins left in your account\nPlease Play Again"

        while len(result) > 2000:
            random_emojis.pop()
            result = " ".join(random_emojis)
            play_again_text = (f"*(message above was truncated since {number} exceeds the max length of 2000"
                               f" characters)*\n{user_balance} coins left in your account\nPlease Play Again")

        if number <= 0:
            await ctx.reply("What did you think would happen uh?")
            return
        
        await ctx.reply(result)

        result_text = play_again_text

        if number == 1:
            await ctx.send("You won! wait...")
        elif all(emoji == random_emojis[0] for emoji in random_emojis):
            probability = 1 / (len(emojis_list) ** (number - 1))
            percentage = probability * 100
            winnings = calculate_winnings(len(emojis_list), number)
            result_text = (f"You won! The probability of winning was {percentage:.2f}% (1 in {int(1 / probability)}).\n{winnings} "
                           f"coins were added to your balance. {user_balance + winnings} coins left in your account.")
            await add_balance(user_id, guild_id, winnings)

        await ctx.send(result_text)


async def setup(bot) -> None:
    await bot.add_cog(Slots(bot))

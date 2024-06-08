from discord.ext import commands
import random
from api.utils import get_balance, calculate_winnings, add_balance, deduct_balance
import time


class Slots(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="slots", description="Slots through server emojis", with_app_command=True)
    async def command(self, ctx, number: int = 3):
        user_id = ctx.author.id
        cost_per_play = 5

        if get_balance(user_id) < cost_per_play:
            await ctx.reply("You don't have enough coins to play.")
            return

        deduct_balance(user_id, cost_per_play)

        emojis = ctx.message.guild.emojis
        emojis_list = [str(emoji) for emoji in emojis]
        random_emojis = random.choices(emojis_list, k=number)
        result = " ".join(random_emojis)
        play_again_text = f"{get_balance(user_id)} coins left in your account\nPlease Play Again"
        
        while len(result) > 2000:
            random_emojis.pop()
            result = " ".join(random_emojis)
            play_again_text = (f"*(message above was truncated since {number} exceeds the max length of 2000"
                               f" characters)*\n{get_balance(user_id)} coins left in your account\nPlease Play Again")
            
        if number <= 0:
            await ctx.reply("What did you think would happen uh?")
            return
        else:
           await ctx.reply(result)
        
        if number == 1:
            await ctx.send("You won! wait...")
        if all(emoji == random_emojis[0] for emoji in random_emojis):
            probability = 1 / (len(emojis_list) ** (number-1))
            percentage = probability * 100
            winnings = calculate_winnings(len(emojis_list), number)
            add_balance(user_id, winnings)
            await ctx.send(f"You won! The probability of winning was {percentage:.2f}% (1 in {int(1/probability)}).\n{winnings}"
                           f" coins were added to your balance. {get_balance(user_id)} coins left in your account.")
        else:
            await ctx.send(play_again_text)


async def setup(bot) -> None:
    await bot.add_cog(Slots(bot))

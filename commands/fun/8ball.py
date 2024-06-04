import discord
from discord.ext import commands
import random

class Eightball(commands.Cog):
    def __init__(self, bot) -> None:
        self.bot = bot

    @commands.hybrid_command(name="8ball", description="Ask the bot what he thinks about your question!", with_app_command=True)
    async def command(self, ctx, *, question):
        if question.split()[0].lower() == "when":
            when = [
                'Now.',
                'Right now.',
                'In a few minutes only!',
                'Just wait a few more hours.',
                'Sometime today.',
                'Today.',
                'At midnight.',
                'Tomorrow.',
                'Surely tomorrow.',
                'Tomorrow, possibly at the end of the day.',
                'Possibly tomorrow, if not, after tomorrow',
                'Possibly in a few days.',
                'Wait a few more days.',
                'After tomorrow!',
                f'This {random.choice(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"])}.',
                'Next week!',
                'Just wait until next week rolls around!',
                f'In exactly {random.randrange(0, 31)} days.',
                'Most likely in a few weeks only.',
                'Probably only next month.',
                'Just wait until next month!',
                'Next month!',
                'Next year :P',
                'Just wait until the new year comes around!',
                'Just be patient man!',
                'Never.',
                'Most likely never.',
                'That will happen when pigs fly :P',
                'Not in a month of Sundays! :P',
                "It won't happen.",
                'God knows when.',
                'Why are you asking? Just wait.',
                'Have you heard of waiting?'
            ]

            reply = random.choice(when)
            embed_color = discord.Color.from_rgb(0, 0, 204)

        else:
            yes_no = [
                'Yes.',
                'Yes, surely.',
                'It is common knowledge that the answer is yes.',
                'Absolutely!',
                'Most likely',
                'My sources point to yes.',
                'It is certain.',
                'Without the shadow of a doubt!',
                'Outlook good',
                'Signs point to yes.',
                'You may rely on it.',
                'Count on it!',

                'Maybe, maybe not.',
                "Can't predict right now.",
                'Concentrate and ask again.',
                'I better not tell you right now!',
                'Reply hazy, try again mate.',
                'Try again later.',

                'No.',
                'No, surely not.',
                'Everyone knows the answer is no!',
                'Absolutely not!',
                'Most likely not',
                'My sources point to no.',
                'Certainly not.',
                'Very doubtful...',
                'Outlook not so good.',
                'Evidence points to no.',
                "Don't rely on it.",
                "Don't even think about it."

            ]

            reply = random.choice(yes_no)

            if reply in yes_no[0:12]: # Positive
                embed_color = discord.Color.green()

            elif reply in yes_no[12:18]: # Neutral
                embed_color = discord.Color.yellow()

            else: # Negative
                embed_color = discord.Color.red()

        embed = discord.Embed(color=embed_color)
        embed.add_field(name=f":question: {ctx.author.display_name} asked...", value=question, inline=False)
        embed.add_field(name=f":8ball: responds...", value=reply, inline=False)


        await ctx.send(embed=embed)


async def setup(bot) -> None:
    await bot.add_cog(Eightball(bot))
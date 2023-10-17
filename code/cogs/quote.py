import discord
import random
import alphonse_utils as AlphonseUtils
from discord.ext import commands
 

class Wisdom(commands.Cog):

    """
    This deals with novely commands.
    TODO:
    - implement haiku generator.
    """

    break_command = "<break>"

    @commands.command()
    async def wisdom(self, ctx):
    """
    RENAME ME TO MOOD AND SYNC UP MOOD W ME.
    """
        with open("data/newquote.txt", mode="r") as f:
            data = f.read().split(self.break_command)
            chosen = random.choice(data)
            await ctx.send(chosen)

    @commands.command(name='quote.submit')
    async def quote_submit(self, ctx):
        """
        Consider having quote.submit feed immediately into data.active_quotes.quotes. If that, then give me
        commands to delete quotes. Remember to make this also process responses.
        """
        quote = None
        author = None
        if ctx.message.reference is not None:
            reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            quote = reply.content
            author = reply.author.nick
        else:
            quote = ctx.message.content.replace(ctx.prefix + ctx.command.name, "")
            author = ctx.message.author.nick

        with open("data/newquote.txt", mode="a") as f:
            f.write(quote + "\n\t -" + author + "\n" + self.break_command)
        await AlphonseUtils.affirmation(ctx)

async def setup(bot):
    await bot.add_cog(Wisdom(bot))

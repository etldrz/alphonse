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
        Spits out a quote that has been given to Alphonse via `!quote.submit`
        """
        
        with open("data/newquote.txt", mode="r") as f:
            data = f.read().split(self.break_command)
            chosen = random.choice(data)
            await ctx.send(chosen)

    @commands.command(name='quote.submit')
    async def quote_submit(self, ctx):
        """
        Takes the inputted text (or reaction text) and feeds it into a file which `!wisdom` draws from.
        """
        
        quote = None
        author = None
        if ctx.message.reference is not None:
            reply = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            quote = reply.content
            author = reply.author.nick
            if author is None:
                author = reply.author.global_name
        else:
            quote = ctx.message.content.replace(ctx.prefix + ctx.command.name, "")
            author = ctx.message.author.nick
            if author is None:
                author = ctx.message.author.global_name

        with open("data/newquote.txt", mode="a") as f:
            f.write(self.break_command + quote + "\n\t -" + author + "\n")
        await AlphonseUtils.affirmation(ctx)

async def setup(bot):
    await bot.add_cog(Wisdom(bot))

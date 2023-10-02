import discord
from discord.ext import commands

class MostDangerousGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def midge(self, ctx):
        await ctx.send("goddamnit")
        

async def setup(bot):
    await bot.add_cog(MostDangerousGame(bot))

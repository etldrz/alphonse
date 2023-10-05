import discord
import time
from discord.ext import commands
from discord.ext import tasks

class MostDangerousGame(commands.Cog):
    

    def __init__(self, bot):
        self.bot = bot
        self.already_running = False
        self.time = 48
        self.scoreboard = dict()

    def add_point(self, user_id):
        curr_keys = self.scoreboard.keys()
        for k in curr_keys:
            if user_id == k:
                self.scoreboard[k] += 1
                return
        self.scoreboard[user_id] = 1

    
    # def order_points(self):
    #     #


    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id = 1153007466297172129 #lackluster-bluster
        channel = self.bot.get_channel(channel_id)
        
        if not self.already_running or message.channel.id != channel_id or message.author.id == self.bot.user.id:
            return

        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if attachment.content_type.split("/")[0] == "image":
                    self.add_point(message.author.id)
                    await channel.send("gottem")


    @commands.command()
    async def midge(self, ctx):
        """
        Coerces inputted floats into int.
        """
        
        text = ctx.message.content.split(" ")
        del text[0]

        if not self.already_running:
            self.already_running = True
        else:
            await ctx.send("The command has already been called. Please wait for the current"\
                           " contest to finish before creating another one.")
            return
        
        if len(text) > 0 and text[0].isnumeric():
            time = int(text[0])


async def setup(bot):
    await bot.add_cog(MostDangerousGame(bot))

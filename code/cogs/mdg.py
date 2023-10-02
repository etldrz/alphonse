import discord
import time
from discord.ext import commands
from discord.ext import tasks

class MostDangerousGame(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.already_running = False
        self.time = 48

    @commands.Cog.listener()
    async def on_message(self, message):
        channel_id = 1153007466297172129
        channel = self.bot.get_channel(channel_id)
        
        if not self.already_running or message.channel.id != channel_id: #lackluster-bluster
            return

        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if attachment.content_type.split("/")[0] == "image":
                    await channel.send("woo doggy")
        


    @commands.command()
    async def midge(self, ctx):
        """
        Will coerce floats into int.
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


    @tasks.loop(seconds=10, count=1)
    async def testing(self):
        print("zzzzzzz")

    @testing.after_loop
    async def after(self):
        await ctx.send("All done.")
           


            

async def setup(bot):
    await bot.add_cog(MostDangerousGame(bot))

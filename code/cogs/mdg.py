import discord
import time
import alphonse_utils as AlphonseUtils
from discord.ext import commands
from discord.ext import tasks

class MostDangerousGame(commands.Cog):
    """
    When '!most.dangerous.game TIME' is called, this class tracks every instance of a picture
    in a specified channel and logs points to users who send in the pictures. At the end, the top three scorers are
    announced. If TIME is not specified, 48 hours is used. Only one contest can be running at a time.

    TODO:
    - Add a command to deprecate points from a specified user (as a safety)
    - Add a command to add points
    - Add a function to see the entire score
    """

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
                    await message.add_reaction(AlphonseUtils.affirmative)


                    
    
    @commands.command()
    async def add(self, ctx):
        """
        Adds a point to a named user.
        """
        if not AlphonseUtils.check_if_personal(ctx):
            return
        text = ctx.message.content.split(" ")
        del text[0]
        if len(text) == 0:
            await AlphonseUtils.personal_id.send("Bad add command.")
        name = " ".join(text)
        person = None
        for m in ctx.guild.members:
            if m.name == name or m.nick == name or m.global_name == name:
                person = m
                break
        if person is None:
            await AlphonseUtils.personal_id.send("Bad name specification.")
            return

        self.add_point(person.id)
        await AlphonseUtils.affirmation(ctx)

            

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
        
        self.scoreboard.clear() #resets from previous contests

        if len(text) > 0 and text[0].isnumeric():
            time = int(text[0])


async def setup(bot):
    await bot.add_cog(MostDangerousGame(bot))

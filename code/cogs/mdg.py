import discord
import alphonse_utils as AlphonseUtils
from datetime import datetime, timedelta, time
from zoneinfo import ZoneInfo
from discord.ext import commands, tasks

class MostDangerousGame(commands.Cog):
    """
    When '!most.dangerous.game TIME' is called, this class tracks every instance of a picture
    in a specified channel and logs points to users who send in the pictures. At the end,
    the top three scorers are announced. If TIME is not specified, 48 hours is used. Only
    one contest can be running at a time.
    """


    current_context = None #used by the task to send messages to the chat it was called in.
    time = 2 #the default n units of time the contest runs for
    starting = False #used by the task to ignore the first call, since, with a count of 2, the task runs
                     #once when starting and once after time has elapsed.
    previous_results = dict()
    result_message_id = 0


    def __init__(self, bot):
        self.bot = bot
        self.scoreboard = {AlphonseUtils.personal_id: 3, 1150550371123593287: 1, 1150523334094753832: 2}
        self.contest_channel = self.bot.get_channel(1164419805525323908)


    def add_point(self, user_id, count):
        """
        Adds an amount of points equal to count to the specified user.
        """
        
        for k in self.scoreboard.keys():
            if user_id == k:
                self.scoreboard[k] += count
                return
        self.scoreboard[user_id] = count


    async def on_end(self, ctx):
        """
        Deals with end of contest message and cleaning up.
        """
        
        self.previous_results.clear()
        if len(self.scoreboard) == 0:
            return
        
        for k in self.scoreboard.keys():
            curr_member = await AlphonseUtils.get_member(ctx, str(k))
            if curr_member is None:
                continue
            curr_nick = curr_member.nick
            if curr_nick is None:
                curr_nick = curr_member.global_name
            self.previous_results[curr_nick] = str(self.scoreboard[k])
            
        self.previous_results = dict(sorted(self.previous_results.items(), key=lambda x:x[1], reverse=True))

        message = "The contest has ended! Here are top players "
        count = 0
        gold = []
        runners_up = []
        for i in self.previous_results.items():
            if count == 3:
                break
            if len(gold) == 0:
                gold.append(i)
                count += 1
            elif i[1] == gold[0][1]:
                gold.append(i)
            else:
                runners_up.append(i)
                count += 1

        if len(gold) == 0 or int(gold[0][1]) <= 0:
            await AlphonseUtils.dm_error(current_ctx,
                                         message="The #fencer-spotted contest either had a population of zero, "\
                                         "or the winner(s) had less-than or equal-to zero points::"\
                                         + "\n'MostDangerousGame.on_end'")
            return

        message += "\nIn first place:\n"
        for g in gold:
            message += "- " + g[0] + " at " + g[1] + " points\n"
            
        if len(runners_up) > 0:
            message += "With runners up of:\n"
            for r in runners_up:
                message += "- " + r[0] + " at " + r[1] + " points\n"
            if len(runners_up) + len(gold) < len(self.previous_results):
                message += "To see a complete list of the players, add a reaction to this message."
                results = await ctx.send(message)
                self.result_message_id = results.id
                return
            else:
                results = await self.contest_channel.send(message)
                return

        self.result_message_id = 0
        await self.contest_channel.send(message)
        
        
    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        """
        When users react to the message Alphonse releases at the end of the contest, the entire scoresheet will
        be DM'd to them, provided there are more than three participants (the max amount the end of contest
        message will announce).
        """
        
        if reaction.message.id != self.result_message_id:
            return

        message = "Here are all the people who participated:\n"
        for i in self.previous_results:
            message += "- " + i[0] + " at " + i[1] + " points\n"
        await user.send(message)


    @commands.Cog.listener()
    async def on_message(self, message):

        if not self.contest.is_running() \
           or message.channel.id != self.contest_channel.id \
               or message.author.id == self.bot.user.id:
            return

        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if attachment.content_type.split("/")[0] == "image":
                    self.add_point(message.author.id, 1)
                    await message.add_reaction(AlphonseUtils.affirmative)


    @commands.command(name="change.channel")
    async def change_channel(self, ctx):
        if not AlphonseUtils.check_if_personal(ctx):
            return

        text = ctx.message.content.split(" ")
        del text[0]

        if len(text) == 0:
            await ctx.send("Bad call.")
            return

        server_name = " ".join(text)

        channels = ctx.guild.text_channels

        for c in channels:
            if c.name == server_name:
                self.contest_channel = c
                await AlphonseUtils.affirmation(ctx)
                return

        await AlphonseUtils.dm_error(ctx, message="The channel does not exist in the guild: " + ctx.guild.name\
                                     + "::\n 'MostDangerousGame.change_channel'")


    @commands.command(name="kill.contest")
    async def kill_contest(self, ctx):
        """
        Ends the current contest.
        """
        
        if not AlphonseUtils.check_if_personal(ctx):
            return
        self.contest.cancel()

    
    @commands.command(name="add.point")
    async def add_point(self, ctx):
        """
        Adds a point to a named user.
        """
        if not AlphonseUtils.check_if_personal(ctx):
            return
        text = ctx.message.content.split(" ")
        del text[0]
        if len(text) == 0:
            await AlphonseUtils.dm_error(ctx, message="No member was specified::" \
                                           "\n 'MostDangerousGame.add'")
            return
        
        name = " ".join(text)
        person = await AlphonseUtils.get_member(ctx, name)
        if person is None:
            return
        self.add_point(person.id, 1)
        await AlphonseUtils.affirmation(ctx)
        

    @commands.command(name="rem.point")
    async def rem_point(self, ctx):
        """
        Removes a point from the named user.
        """

        if not AlphonseUtils.check_if_personal(ctx):
            return
        text = ctx.message.content.split(" ")
        del text[0]
        if len(text) == 0:
            await AlphonseUtils.dm_error(ctx, message="No member was specified::" \
                                         "\n 'MostDangerousGame.dep'")
            return
        name = " ".join(text)
        person = await AlphonseUtils.get_member(ctx, name)
        if person is None:
            return

        self.add_point(person.id, -1)
        await AlphonseUtils.affirmation(ctx)


    @commands.command(name="friendship.killer")
    async def friendship_killer(self, ctx):
        """
        Starts a contest for #fencer-spotted.
        """
        
        text = ctx.message.content.split(" ")
        del text[0]

        if self.contest.is_running():
            await ctx.send("The command has already been called. Please wait for the current"\
                           " contest to finish before creating another one.")
            return
        
        if len(text) > 0 and text[0].isnumeric():
            user_time = int(text[0])
            delta = 0 if (user_time - self.time < 0) else (user_time - self.time)
            self.time += delta
            await ctx.send("triggered")
            await ctx.send(delta)

        self.scoreboard.clear() #resets from previous contests

        self.current_context = ctx
        self.starting = True
        self.contest.start()


    @tasks.loop(hours=time, count=2)
    async def contest(self):
        """
        Deals with how long the contest will run for.
        """
        
        if self.starting:
            message = "The contest to spot as many of your peers as possible has just begun. Each picture "\
                "that you post into this channel will automatically earn you a point; the results will be "\
                "released at the end of the contest. "\
                "You have " + str(self.time) + " hours to spot as many fencers as possible.\n\n"\
                "Since all I can do is notice that an image has been "\
                "posted, please don't post images to this channel unless they have a fencer in them. \n\n\n"\
                "Good hunting."
            
            await self.contest_channel.send(message)
            self.starting = False
            return

        await self.on_end(self.current_context)


async def setup(bot):
    await bot.add_cog(MostDangerousGame(bot))

import discord
from discord.ext import commands
from datetime import date, datetime
from pytz import timezone
import alphonse_utils as AlphonseUtils



class Analysis(commands.Cog):

    

    def __init__(self, bot):
        self.bot = bot
        self.fall_start = [8, 10] #month, day
        self.spring_start = [1, 10] #month, day
        self.fall_months = [8, 9, 10, 11, 12]
        self.spring_months = [1, 2, 3, 4, 5]


    @commands.command(name="new.members")
    async def new_members(self, ctx):
        today = date.today()
        curr_year = today.year
        curr_month = today.month

        is_fall = None
        if curr_month in self.fall_months:
            is_fall = True
        elif curr_month in self.spring_months:
            is_fall = False
        elif curr_month < self.fall_months[0]:
            is_fall = False
        else:
            await ctx.send("You are not currently in either Spring or Fall semester, your data could be bad.")
            is_fall = True

        start_date = datetime(curr_year, month=self.fall_start[0], \
                              day=self.fall_start[1], tzinfo=timezone('US/Eastern'))
        if not is_fall:
            start_date = datetime(curr_year, self.spring_start[0], \
                                  self.spring_start[1], tzinfo=timezone('US/Eastern'))

        new_members = []
        for m in ctx.guild.members:
            if m.joined_at > start_date:
                new_members.append(m)

        await self.role_sort(ctx, new_members)


        



    async def role_sort(self, ctx, members):

        if len(members) == 0:
            await AlphonseUtils.dm_error(ctx, message="The members list is 0::"\
                                         "\n'Analysis.role_sort'")
            return

        message = "There have been " + str(len(members)) + " additions to " + ctx.guild.name + \
        " within this semester (or the most previous one). The data isn't currently set up to be saved; if you want to save it "\
        "then do it yourself."


        data = dict()
        for role in ctx.guild.roles:
            count = 0
            
            for member in members:
                name = role.name
                if role.name == "@everyone":
                    name = "everyone"
                if role in member.roles:
                    count += 1
            data[name] = count

        message += "\n\nOf those new members,"

        for d in data.items():
            message += "\n- " + str(d[1]) + " are " + d[0]


        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Analysis(bot))
        
        

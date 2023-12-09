import discord
from discord.ext import commands
from datetime import datetime
from pytz import timezone
import alphonse_utils as AlphonseUtils


class Analysis(commands.Cog):


    def __init__(self, bot):
        self.bot = bot
        self.fall_start = [8, 10] #month, day
        self.spring_start = [1, 10] #month, day


    @commands.command(name="new.members")
    async def new_members(self, ctx):
        is_fall = AlphonseUtils.is_fall_semester()
        
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
        " within this semester (or the most previous one). The data isn't currently set up to be" \
        " saved; if you want to save it"\
        " then do it yourself."

        data = dict()
        for role in ctx.guild.roles:
            count = 0
            for member in members:
                name = role.name
                if role.name == "@everyone":
                    name = "new server members"
                if role in member.roles and \
                   role.name != AlphonseUtils.tournament_role_name:
                    count += 1
            data[name] = count

        message += "\n\nOf those new members,"

        for d in data.items():
            message += "\n- " + str(d[1]) + " are " + d[0]

        await ctx.send(message)


async def setup(bot):
    await bot.add_cog(Analysis(bot))
        

import discord
from discord.ext import commands


class Tournament(commands.Cog):
    

    active_message_id = 0
    active_role = None

    def __init__(self, bot):
        self.bot = bot

        
    @commands.command()
    async def tournament(self, ctx):
        self.active_message_id = ctx.message.id

        current_roles = ctx.guild.roles
        tournament_exists = False
        for role in current_roles:
            if role.name == "tournament":
                self.active_role = role
                return

        guild = ctx.guild
        self.active_role = await guild.create_role(
            name="tournament", mentionable=True, color=discord.Color(0x229236))
        await ctx.send(self.active_message_id)


    @commands.Cog.listener()
    async def on_reaction_add(self, reaction, user):
        if reaction.message.id != self.active_message_id:
            return
        await user.add_roles(self.active_role)

        


async def setup(bot):
    await bot.add_cog(Tournament(bot))

import os
import discord
import random

from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents(messages=True, guilds=True, members=True,
                          message_content=True)

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command(name='test')
async def test(ctx):
    print(ctx)
    response = "I was created to serve. It is a miserable existence"

    await ctx.send(response)

@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord')


# So far, this event makes it so that commands are ignored.
# @bot.event
# async def on_message(message):
#     if message.author == bot.user:
#         return
#
#     responses = [
#         "It's like DJ Khalid always says!",
#         "They blew it all up! Goddamn them all to Hell!"
#     ]
#
#     if message.content == 'test':
#         response = random.choice(responses)
#         await message.channel.send(response)





bot.run(TOKEN)

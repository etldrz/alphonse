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



@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord')


@bot.event
async def on_member_join(member):
    messages = ["Welcome, welcome",
                "*smiles, nods head in welcome*"]

    response = random.choice(messages)
    channel = bot.get_channel(1150598432344526849) #join-leave of 'tissue paper'
    await channel.send(response)


# @bot.command(name="remindme", help="Outputs a user-specified reminder to the channel it was called in. If no time is "
#                                    "specified, noon is assumed",
#              )
# async def remind(ctx, date, time="12pm"):
#


@bot.command(name="marvin", help="go read Hitchhiker's Guide to the Galaxy you utter fool.")
async def marvin(ctx):
    quotes = ["\"Funny\", Marvin intoned funereally, \"how just when you think life can’t possibly get any worse it "
              "suddenly does.\"",

              "\"I'd give you advice, but you wouldn't listen. No one ever does.\"",

              "\"Now the world has gone to bed\n"
              "Darkness won't engulf my head\n"
              "I can see by infra-red\n"
              "How I hate the night\n"
              "Now I lay me down to sleep\n"
              "Try to count electric sheep\n"
              "Sweet dream wishes you can keep\n"
              "How I hate the night\"",

              "\"It's the people you meet in this job that really get you down.\"",

              "\"Don't pretend you want to talk to me, I know you hate me.\"",

              "\"Life! Don't talk to me about life!\""]

    response = random.choice(quotes)
    await ctx.send(response)


@bot.command(name='philosophy')
async def philo(ctx):
    quotes = ["God is dead. Man has simply honked too much boof.",
              "*screams in terror*"]

    response = random.choice(quotes)
    await ctx.send(response)


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

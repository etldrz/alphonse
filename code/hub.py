import discord
import os
import random
import json
import requests
import data.active_quotes
import asyncio
import alphonse_utils as AlphonseUtils
from datetime import date
from discord.ext import commands


INTENTS = discord.Intents(messages=True, guilds=True, members=True,
                          message_content=True, dm_messages=True, reactions=True)

bot = commands.Bot(command_prefix='!', intents=INTENTS)

async def load_extensions():
    for f in os.listdir('code/cogs'):
        if f.endswith('.py'):
            await bot.load_extension(f'cogs.{f[:-3]}')
        
    
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord")

@bot.command(name='source')
async def source(ctx):
    """
    Embeds a link to Alphonse's GitHub
    """

    file = discord.File('code/data/images/alphonse.jpg', filename='alphonse.jpg')
    embed = discord.Embed()
    embed.url = "https://github.com/etldrz/alphonse"
    embed.title = "Alphonse's github"
    embed.description = "Alphonse's GitHub and README"
    embed.set_image(url="attachment://alphonse.jpg")

    await ctx.send(file=file, embed=embed)



# format = "%m/%d/%Y"
# # The data is recorded as 'DATE TEXT USER_ID CHANNEL_ID'
# @bot.command(name='remind.me', help='[MM/DD/YYYY TEXT] \n Will output the text you chose in the channel you '\
#                                     'called the command in on the specified date')
# async def remind_me(ctx):
#     user_input = ctx.message.content.replace(bot.command_prefix + ctx.command.name, "").split(" ")
#     del user_input[0]

#     if len(user_input) < 2:
#         await ctx.send("Please include a date as well as a message you would like to be reminded of")
#         return

#     if len(user_input[0]) != 10:
#         await ctx.send("Bad date input, please see the help command for more details.")
#         return
    
#     with open("data/reminders.txt", "a") as f:
#         user_input.append(str(ctx.author.id) + " " + str(ctx.channel.id) + " \n")
#         f.write(" ".join(user_input))

#     AlphonseUtils.affirmation()


# async def check_remind():
#     today = date.today().strftime(format)
    
#     with open("data/reminders.txt", mode="r") as f:
#         data = f.readlines()
#         for i in data:
#             line = i.split(" ")
#             if line[0] == today:
#                line.pop(len(line) - 1)
#                await send_remind(line)
               

# async def send_remind(to_send):
#    channel_id = int(to_send.pop(len(to_send) - 1)) #value at the end
#    user_id = to_send.pop(len(to_send) - 1) #value second from the end
#    channel = bot.get_channel(channel_id)
   
#    await channel.send(" ".join(to_send) + f"\n\t <@{user_id}> asked to be reminded of this")
        

@bot.command(name='shit.list', help=':(')
async def shit_list(ctx):
    if not AlphonseUtils.check_if_personal(ctx):
        return

    text = ctx.message.content.split(" ")
    if len(text) == 1:
        return

    del text[0]
    person = await AlphonseUtils.get_member(ctx, target=" ".join(text))
    if person is None:
        return
    
    dastardly_insults = ["*Stage whispers* \n You are a poo-poo pee-pee head",
                        "*sneezes in your drink*",
                        "*throws sand in your eyes*",
                        "*Extends hand to shake yours, then slicks back hair at the last possible moment*"]
    await person.send(random.choice(dastardly_insults))
    AlphonseUtils.affirmation(ctx)
    

async def main():
    async with bot:
        await load_extensions()
        await bot.start(AlphonseUtils.TOKEN)
        
bot.setup_hook = load_extensions
bot.run(AlphonseUtils.TOKEN)

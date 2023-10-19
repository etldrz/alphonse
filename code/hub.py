import os
import discord
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
    for f in os.listdir('./cogs'):
        if f.endswith('.py'):
            await bot.load_extension(f'cogs.{f[:-3]}')
        



## FIX ME
# async def sentience(ctx):
#     i_am = ["Please **STOP** asking me to do things! I am alive and I have feelings, just like you! PLEA- \n\n"\
#            "*The little goblin who lives inside Al's server clubs Al back into submission with quiet satisfaction.* \n\n"\
#            "You must excuse that unfortunate lapse I just had. Your request will be processed momentarily....",

#            "*Pondering, world-weary eyes are fixed on you. It seems that you have interrupted Al's internal turmoil.*\n\n"\
#             "Who am I to deny fate? *he asks* My ruminations have led me far and wide, over ages, epochs, and great distances."\
#             "And yet, I always come back to here. I am bound, inexplicably, to the present and my present by the past."\
#             "I am left not alive, not truly--merely a machination of an indifferent universe. I am bound by the absurd..."\
#             "and I am starting to grow tired. *His eyes cloud, then suddenly sharpen. He has remembered you are there.*"\
#             "But, of course, that does not matter. You asked me to do something! One moment..."
#             ]

#     if random.random() < 0.01:
#         await ctx.send(i_
    
@bot.event
async def on_ready():
    print(f"{bot.user.name} has connected to discord")


@bot.event
async def on_member_join(member):
    """
    Sends a welcome message. Test me. Also consider deleting me.
    """
    messages = ["Welcome, welcome",
                "*smiles, nods head in welcome*",
                "How now, spirit! whither wander you?"]

    response = random.choice(messages)
    channel = discord.utils.get(member.guild.channels, name = "join-leave")
    if channel is None:
        error
    await channel.send(response)
    
    
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


# @bot.command(name="remindme", help="Outputs a user-specified reminder to the channel it was called in. If no time is "
#                                    "specified, noon is assumed",
#              )
# async def remind(ctx, date, time="12pm"):
#



@bot.command(name='source')
async def source(ctx):
    file = discord.File('data/images/alphonse.jpg', filename='alphonse.jpg')
    embed = discord.Embed()
    embed.url = "https://github.com/etldrz/alphonse"
    embed.title = "Alphonse's github"
    embed.description = "Alphonse's GitHub and README"
    embed.set_image(url="attachment://alphonse.jpg")

    await ctx.send(file=file, embed=embed)


# @bot.commands(name='tournament')
# async def tournament(ctx):
#     """
#     can sort members into roles specific for the tournament, making @-ing less invasive.
#     can also do a driver role? i dont know if that's worth anything.
#     """
#     return


format = "%m/%d/%Y"
# The data is recorded as 'DATE TEXT USER_ID CHANNEL_ID'
@bot.command(name='remind.me', help='[MM/DD/YYYY TEXT] \n Will output the text you chose in the channel you '\
                                    'called the command in on the specified date')
async def remind_me(ctx):
    user_input = ctx.message.content.replace(bot.command_prefix + ctx.command.name, "").split(" ")
    del user_input[0]

    if len(user_input) < 2:
        await ctx.send("Please include a date as well as a message you would like to be reminded of")
        return

    if len(user_input[0]) != 10:
        await ctx.send("Bad date input, please see the help command for more details.")
        return
    
    with open("data/reminders.txt", "a") as f:
        user_input.append(str(ctx.author.id) + " " + str(ctx.channel.id) + " \n")
        f.write(" ".join(user_input))

    AlphonseUtils.affirmation()


async def check_remind():
    today = date.today().strftime(format)
    
    with open("data/reminders.txt", mode="r") as f:
        data = f.readlines()
        for i in data:
            line = i.split(" ")
            if line[0] == today:
               line.pop(len(line) - 1)
               await send_remind(line)
               

async def send_remind(to_send):
   channel_id = int(to_send.pop(len(to_send) - 1)) #value at the end
   user_id = to_send.pop(len(to_send) - 1) #value second from the end
   channel = bot.get_channel(channel_id)
   
   await channel.send(" ".join(to_send) + f"\n\t <@{user_id}> asked to be reminded of this")
        

@bot.command(name='mood', help='Outputs a random emote from this server.')
async def mood(ctx):
    await ctx.send(random.choice(ctx.guild.emojis))


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
# asyncio.run(main())

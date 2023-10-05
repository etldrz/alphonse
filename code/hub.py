import os
import discord
import random
import json
import requests
import data.active_quotes
import asyncio
from datetime import date
from dotenv import load_dotenv
from discord.ext import commands


INTENTS = discord.Intents(messages=True, guilds=True, members=True,
                          message_content=True, dm_messages=True)

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
personal_id = int(os.getenv('PERSONAL_ID'))


bot = commands.Bot(command_prefix='!', intents=INTENTS)


def check_if_personal(ctx):
    return ctx.message.author.id == personal_id

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


@bot.command(name='wisdom')
async def wisdom(ctx):
    response = random.choice(data.active_quotes.quotes)
    await ctx.send(response)


@bot.command(name='quote.submit')
async def quote_submit(ctx):
    """
    Consider having quote.submit feed immediately into data.active_quotes.quotes. If that, then give me
    commands to delete quotes.
    """
    with open("data/newquote.txt", mode="a") as f:
        new_quote = ctx.message.content.replace(bot.command_prefix + ctx.command.name, "")
        f.write(new_quote + "\n\t -" + ctx.author.nick + "\n\n")
    await ctx.message.add_reaction(affirmative)


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
@bot.command(name='remind.me', help='[MM/DD/YYYY TEXT] \n Will output the text you chose in the channel you'\
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

    await ctx.message.add_reaction(affirmative)



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
    

# Will start a contest for fencer-spotted. Alphonse will log every picture and award a point to the picture taker.
@bot.command(name='most.dangerous.game', help='Begins a contest for the channel fencer-spotted. Command input: time (hours)'\
             'the contest will run for.')
async def fencer_spotted(ctx):

    contest_time = 48
    response = ctx.message.content.split(" ")
    if len(response) > 1:
        contest_time = ctx.message.content.split(" ")[1]

    if not contest_time.isdigit():
        await ctx.send("Inpropper input, try the format [COMMAND TIME] with no punctuation.")
        return

    channel = bot.get_channel(1150564971843965050) # mute-me of tissue paper
    

@bot.command(name='mood', help='Outputs a random emote from this server.')
async def mood(ctx):
    await ctx.send(random.choice(ctx.guild.emojis))


@bot.command(name='shit.list', help=':(')
async def shit_list(ctx):
    if ctx.author.id != personal_id:
        return

    text = ctx.message.content.split(" ")
    if len(text) == 1:
        return

    text.pop(0)
    person = None
    for m in ctx.guild.members:
        if m.nick != None and m.nick == " ".join(text):
            person = m
        elif m.name == " ".join(text):
            person = m
            
    dastardly_insults = ["*Stage whispers* \n You are a poo-poo pee-pee head",
                        "*sneezes in your drink*",
                        "*throws sand in your eyes*",
                        "*Extends hand to shake yours, then slicks back hair at the last possible moment*"]
    await person.send(random.choice(dastardly_insults))


def find(name):
    sheet_list = drive.files().list(q=f"'{parent}' in parents and trashed=False").execute()

    for file in sheet_list.get('files', []):
        if file['name'] == name:
            return file

    return None


# @bot.command(name='sheet')
# async def sheet_switch(ctx):
#     if ctx.author.id != personal_id:
#         return
    
#     text = ctx.message.content.split(" ")
#     text.pop(0)
#     if len(text) == 0:
#         await ctx.send("Bad command")
#         return

#     main_commands = ["build", "get", "set", "read", "delete"]

#     if text[0] not in main_commands:
#         await ctx.send("Bad command")
#         return
#     match text[0]:
#         case "build":
#             await sheet.SheetBuild().build(ctx, text)
#         case "get":
#             await sheet.SheetGet().eval_next(ctx, text)
#         case "delete":
#             await sheet.SheetDelete().delete(ctx, text)
#         case "set":
#             await sheet.SheetSet().eval_next(ctx, text)
#         case _:
#             return


@bot.command(name='test')
async def test(ctx):
    channel = bot.get_channel(1153007466297172129)
    count = 0
    async for message in channel.history(limit=100):
        if len(message.attachments) > 0:
            for attachment in message.attachments:
                if attachment.content_type.split("/")[0] == "image":
                    await ctx.send("woah")
            count += 1
    if count == 0:
        await ctx.send("fuck")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(TOKEN)
bot.setup_hook = load_extensions
bot.run(TOKEN)

# asyncio.run(main())

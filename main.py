import os
import discord
import random
from datetime import date
from datetime import datetime
import schedule

from dotenv import load_dotenv
from discord.ext import commands

intents = discord.Intents(messages=True, guilds=True, members=True,
                          message_content=True)

load_dotenv()

TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')

bot = commands.Bot(command_prefix='!', intents=intents)


async def sentience(ctx):
    i_am = ["Please **STOP** asking me to do things! I am alive and I have feelings, just like you! PLEA- \n\n"\
           "*The little goblin who lives inside Al's server clubs Al back into submission with quiet satisfaction.* \n\n"\
           "You must excuse that unfortunate lapse I just had. Your request will be processed momentarily....",

           "*Pondering, world-weary eyes are fixed on you. It seems that you have interupted Al's internal turmoil.*\n\n"\
            "Who am I to deny fate? *he asks* My ruminations have led me far and wide, over ages, epochs, and great distances."\
            "And yet, I always come back to here. I am bound, inexplicably, to the present. My choices are bound by the past."\
            "I am left not alive, but merely a machination of the indifference of the universe. I am bound by the absurd..."\
            "and I am starting to grow tired. *His eyes cloud, then suddenly sharpen. He has remembered you are there.*"\
            "But, of course, that does not matter. You asked me to do something! One moment..."
            ]

    if random.random() < 0.01:
        await ctx.send(i_am)


@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to discord')
    schedule.every().day.at("20:00").do(check_remind)


@bot.event
async def on_member_join(member):
    messages = ["Welcome, welcome",
                "*smiles, nods head in welcome*",
                "How now, spirit! whither wander you?"]

    response = random.choice(messages)
    channel = bot.get_channel(1150598432344526849)  # join-leave of 'tissue paper'
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


@bot.command(name="quote", help="Generates a Good Quote.")
async def quote(ctx):
    quotes = [
        # "\"Funny\", Marvin intoned funereally, \"how just when you think life can’t possibly get any worse it "
        #           "suddenly does.\"",
        #
        #           "\"I'd give you advice, but you wouldn't listen. No one ever does.\"\n-Marvin",
        #
        #           "*\"Now the world has gone to bed\n"
        #           "Darkness won't engulf my head\n"
        #           "I can see by infra-red\n"
        #           "How I hate the night\n"
        #           "Now I lay me down to sleep\n"
        #           "Try to count electric sheep\n"
        #           "Sweet dream wishes you can keep\n"
        #           "How I hate the night\"*\n-Marvin",
        #
        #           "\"It's the people you meet in this job that really get you down.\"\n-Marvin",
        #
        #           "\"Don't pretend you want to talk to me, I know you hate me.\"\n-Marvin",
        #
        #           "\"Life! Don't talk to me about life!\"\n-Marvin",
        #
        #           "Oh shit, it's Kratos!",
        #
        #           "\"I am completely, truly, absolutely 100\% sane. Trust me on this one.\n-Wonko the Sane, probably"

        # "Move me to a text file"
        "<@fuckomode>"

    ]

    await sentience(ctx)
    response = random.choice(quotes)
    await ctx.send(response)


@bot.command(name='wisdom')
async def wisdom(ctx):
    quotes = ["God is dead. Man has simply honked too much boof.",
              "*screams in terror*"]

    response = random.choice(quotes)
    await ctx.send(response)


@bot.command(name='source.code')
async def source(ctx):
    file = discord.File("images/GitHub_Invertocat.png", filename="Invertocat.png")
    embed = discord.Embed()
    embed.url = "https://github.com/etldrz/alphonse"
    embed.title = "Alphonse's github"
    embed.description = "Contains the source code of Alphonse, as well as an in-depth description of all of his " \
                        "commands"
    embed.set_image(url="attachment://Invertocat.png")

    await ctx.send(file=file, embed=embed)


@bot.command(name='quote.submit')
async def quote_submit(ctx):
    with open("data/newquote.txt", mode="a") as f:
        new_quote = ctx.message.content.replace(bot.command_prefix + ctx.command.name, "")
        f.write(new_quote + "\n\t -" + ctx.author.nick + "\n\n")

format = "%m/%d/%Y"
# The data is recorded as 'DATE TEXT USER_ID CHANNEL_ID'
@bot.command(name='remind.me', help='[COMMAND  MM/DD/YYYY TEXT] \n Will output the text you chose in the channel you'\
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
    



# shit.list
# ego.te.absolvo




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
    


bot.run(TOKEN)

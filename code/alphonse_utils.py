import os
from dotenv import load_dotenv
from datetime import date, datetime

load_dotenv()
personal_id = int(os.getenv('PERSONAL_ID'))
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
affirmative = '\U0001F44D' #'thumbs up' for successful jobs


#TODO: make a function that formats error messages, to be applied whenever dm_error is called


#The year is divided into two segments, because that is all that VTFC cares about or deals with.
fall_months = [8, 9, 10, 11, 12]
spring_months = [1, 2, 3, 4, 5, 6, 7]


#The role name used by Alphonse when creating a tournament role
tournament_role_name = "tournament"


def check_if_personal(ctx):
    return ctx.message.author.id == personal_id


def is_fall_semester():
    curr_month = date.today().month
    return curr_month in fall_months


async def affirmation(ctx):
    await ctx.message.add_reaction(affirmative)


async def dm_error(ctx, message="uh oh"):
    message += "\n\nCalled via user command: '" + ctx.message.content + "'"
    me = await get_member(ctx, str(personal_id))
    await me.send(message)


async def get_member(ctx, target):
    """
    Checks the target against the member list of the
    guild the command is being called in, and returns
    the member object if they can be ID'd.
    """

    #checks to see if the target is an `@`
    if target[0] == "<" and target[1] == "@":
        target = target[2:-1]

    person = None
    for m in ctx.guild.members:
        if m.name == target \
           or m.nick == target \
           or m.global_name == target \
           or (target.isnumeric() and m.id == int(target)):
            person = m
            break
    if person is None:
        message = "The person could not be found" \
            "--called from 'alponse_utils.get_member'"
        await dm_error(ctx, message)

    return person




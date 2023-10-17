import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD = os.getenv('DISCORD_GUILD')
personal_id = int(os.getenv('PERSONAL_ID'))


affirmative = '\U0001F44D' #Al's reaction to a message when the job is completed successfully.


async def affirmation(ctx):
    await ctx.message.add_reaction(affirmative)


def check_if_personal(ctx):
    return ctx.message.author.id == personal_id


async def dm_error(ctx):
    await ctx.send("uh oh")

async def get_member(ctx, target):
    """
    Checks the target against the member list of the guild the command is being called in, and returns
    the member object if they can be ID'd.
    """
    if target[0] == "<" and target[1] == "@":
        target = target[2:-1]

    person = None
    for m in ctx.guild.members:
        if m.name == target or m.nick == target or m.global_name == target or m.id == int(target):
            person = m
            break
    if person is None:
        await personal_id.send("The target: " + target + " could not be found.")

    return person

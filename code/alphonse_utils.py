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

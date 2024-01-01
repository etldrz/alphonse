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
    message += " via user call: '" + ctx.message.content + "'"
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




class SheetUtils:
    """
    Contains utility functions and values for the sheet.py cog.
    """

    #This is the keyword that users define or use to set the in_use_sheet
    user_keyword_in_use_sheet = "curr"

    #Parent folder where all the sheets are stored.
    parent = "1mGKri2dKu7E28BrN9nVMtU6qBszTt7QC"

    folder_mimetype = "application/vnd.google-apps.folder"

    #This chunk sets the in_use_sheet to be "CURRENT_SEMSTER YEAR"
    semester_fall = "Fall"
    semester_spring = "Spring"
    current_sheet = semester_fall
    if not is_fall_semester(): 
        current_sheet = semester_spring
    in_use_sheet = [current_sheet, str(datetime.today().year)] 




    def get_file(name, drive):
        """
        Returns a sheet based on the inputted name, if that sheet exists. None if otherwise.
        """

        if name == SheetUtils.user_keyword_in_use_sheet:
            name = " ".join(SheetUtils.in_use_sheet)

        try:
            sheet_list = drive.files().list(
                q=f"'{SheetUtils.parent}' in parents and trashed=False"
            ).execute()
        except:
            return None

        subdirectories = []
        for item in sheet_list.get("files", []):
            if item["name"] == name:
                return item
            elif item["mimeType"] == SheetUtils.folder_mimetype:
                subdirectories.append(item)

        #If the above loop fails, then the requested file could be inside one of the sub-directories
        #If the loop becomes slow when there are many subdirectories, it can be made more efficient
        #by focusing on directories that share name features (ie years) with the requested files.
        for sub in subdirectories:
            sub_id = sub["id"]
            try:
                sub_items = drive.files().list(
                    q=f"'{sub_id}' in parents and trashed=False"
                ).execute()
            except:
                continue
            for item in sub_items.get("files", []):
                if item["name"] == name:
                    return item

        return None

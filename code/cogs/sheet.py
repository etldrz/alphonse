import discord
import matplotlib.pyplot as plt
import os
import seaborn as sns
from discord.ext import commands
from datetime import date
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


SCOPES = ['https://www.googleapis.com/auth/spreadsheets',
          'https://www.googleapis.com/auth/drive',
          'https://www.googleapis.com/auth/drive.metadata',
          'https://www.googleapis.com/auth/drive.file']

SERVICE_ACCOUNT_FILE = 'data/sensitive/alphonse-key.json'

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)

parent = '1mGKri2dKu7E28BrN9nVMtU6qBszTt7QC' #Parent file for Google Sheet related commands.

drive = build('drive', 'v3', credentials=credentials)

curr_sheet = "test" # holds the name of the current working sheet

affirmative = '\U0001F44D' #Al's reaction to a message when the job is completed successfully.

curr = ["Fall", "2023"] #setting this as curr until actual method is established


    # inventory_commands = ["inventory", "i"]
    # attendance_commands = ["attendance", "a"]
    # epee = ["epee", "e"]
    # foil = ["foil", "f"]
    # sabre = ["sabre", "saber", "s"]
    # attendance_sheet_order = ["date", "foil", "sabre", "epee"]
    # inventory_types = ["epee", "e", "foil", "f", "sabre", "saber", "s", "epee bodycord", "ebc",
    #                    "foil bodycord", "sabre bodycord", "saber bodycord", "rowbc", "maskcord", "mc"]
    # #rowbc is right of way bodycord.
    # broken = ["broken", "b"]
    # fixed = ["fixed", "fi"]
    




    # inventory_commands = ["inventory", "i"]
    # attendance_commands = ["attendance", "a"]
    # as_text = ["cat"]
    # as_plot = ["plot", "p"]
    # plot_types = ["pie", "bar"]


## the above two chunks are up here to remind me to think about finding a more better way to implement.
## maybe dict?


def find(name):
    if name == "curr":
        name = " ".join(curr)
        
    sheet_list = drive.files().list(q=f"'{parent}' in parents and trashed=False").execute()

    for file in sheet_list.get('files', []):
        if file['name'] == name:
            return file

    return None


async def dm_error(ctx):
    await ctx.send("uh oh")


class Sheet(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
        
    @commands.command()
    async def sheet(self, ctx):
        text = ctx.message.content.split(" ")
        del text[0]
        if len(text) == 0:
            await ctx.send("Bad command")
            return

        main_commands = ["build", "get", "set", "read", "delete"]

        if text[0] not in main_commands:
            await ctx.send("Bad command")
            return
        match text[0]:
            case "build":
                await SheetBuild().build(ctx, text)
            case "get":
                await SheetGet().eval_next(ctx, text)
            case "delete":
                await SheetDelete().delete(ctx, text)
            case "set":
                await SheetSet().eval_next(ctx, text)
            case _:
                return
    
    @commands.command()
    async def att(self, ctx):
        text = ctx.message.content.split(" ")
        text[0] = "attendance"
        if len(text) == 0:
            await ctx.send("Bad command: you need to input data.")
            return
        if text[-1] in ["epee", "e", "foil", "f", "sabre", "saber", "s"]:
            text = text + self.curr
            await ctx.send("Using the in-use sheet: " + " ".join(curr))
        await SheetSet().attendance(ctx, text)

    @commands.command()
    async def inv(self, ctx):
        text = ctx.message.content.split(" ")
        text[0] = "inventory"
        if len(text) == 0:
            await ctx.send("Bad command: you need to input data.")
            return
        if text[-1] in ["broken", "b", "fixed", "f"]:
            text = text + curr
            await ctx.send("Using the in-use sheet: " + " ".join(curr))
        await SheetSet().inventory(ctx, text)
        


class SheetGet:
    
    """
    FORMATTING: get a/i/curr/SHEET_NAME
    IF LAST TWO THEN SHEET EMBED LINKED IS OUTPUTTED
    ELSE:
        r/p
    IF RECENT, THEN RECENT DATA OUTPUTTED AS TEXT
    IF PLOT, THEN:
        pie/bar
    FOR ATTENDANCE AND INVENTORY, THE SHEET NAME WILL BE SPECIFIED AT THE END.
    """

    inventory_commands = ["inventory", "i"]
    attendance_commands = ["attendance", "a"]
    as_text = ["cat"]
    as_plot = ["plot", "p"]
    plot_pie = ["pie"]
    plot_bar = ["bar"]
                  
    async def eval_next(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Please further specify what you want.")
            
        if text[0] == "list":
            await self.list(ctx)
            return
        elif text[0] in self.inventory_commands:
            await self.inventory(ctx, text)
            return
        elif text[0] in self.attendance_commands:
            await self.attendance(ctx, text)
            return
        elif text[0] in self.as_plot:
            await self.plot(ctx, text)
            return
        elif text[0] in self.as_text:
            await self.cat(ctx, text)
            return
        
        exists = find(" ".join(text))
        if exists is None:
            await ctx.send("The requested sheet does not exist in the parent directory.")
            return

        await self.get_link(ctx, text, exists)

    
    async def get_data(self, ctx, spreadsheet_id, pull_range, dim = "ROWS"):
        """
        Is only good for a single range; if multiple ranges are needed for a single get,
        consider using batchGet. Will pull by rows unless specified otherwise.
        googleapi enums for dim: ROWS COLUMNS
        """
        try:
            service = build('sheets', 'v4', credentials=credentials)
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=pull_range, majorDimension=dim
            ).execute()
        except HttpError as err:
            await dm_error(ctx)
            return
        data = result.get('values', [])
        return data


    # async def attendance(self, ctx, text):
        # del text[0]
        # exists = None
        # if len(text) == 0:
        #     await ctx.send("Without specification, curr will be accessed.")
        #     exists = find(Sheet.curr)
        # else:
        #     exists = find(" ".join(text))

            
        # if exists is None:
        #     await ctx.send("Please specify an existing spreadsheet.")
        #     return

        # spreadsheet_id = exists['id']
    
        # #ignoring recent and plot for now

        # pull_length = 150
        # range = "Attendance!A1:E" + str(pull_length)
        # data = await self.get_data(ctx, spreadsheet_id, range)
        
        # if len(data) == pull_length:
        #     await ctx.send("Please switch to a new sheet for future data, this one has too many rows to be "\
        #                    "a single semester of fencing.")
        #     pull_length = pull_length * 3
        #     range = "Attendance!A1:E" + str(pull_length)
        #     data = await self.get_data(ctx, spreadsheet_id, range)
        #     if len(data) == pull_length:
        #         await ctx.send("Data length is: " + pull_length + ". To be safe, this command will no longer be completed. "\
        #                        "Consider using the get command to retrieve the sheet link.")
        #         return
        
        
        # return data


    async def plot(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Please specify [PLOT_TYPE DATA_TYPE SHEET_NAME]")
            return

        plot_type = text[0]
        if plot_type not in self.plot_pie and plot_type not in self.plot_bar:
            await ctx.send("Please specify PLOT_TYPE more better. Allowed responses are '"\
                           + ", ".join(self.plot_pie) + "' and '" + ", ".join(self.plot_bar) + "'.")
            return
        del text[0]

        data_type = text[0]
        if data_type not in self.attendance_commands and data_type not in self.inventory_commands:
            await ctx.send("Bad specification of data type. Allowed responses are '"\
                           + ", ".join(self.attendance_commands) + "' and '" +\
                           ", ".join(self.inventory_commands) + "'.")
            return
        del text[0]
        
        exists = find(" ".join(text))
        if exists == None:
            await ctx.send("Please specify a valid sheet name.")
            return

        data = None
        if data_type in self.attendance_commands:
            row_range = "75"
            pull_range = "Attendance!A1:E" + row_range
            data = await self.get_data(ctx, exists['id'], pull_range, "COLUMNS")
        elif data_type in self.inventory_commands:
            row_range = "6"
            pull_range = "Inventory!A1:B" + row_range
            data = await self.get_data(ctx, exists['id'], pull_range, "ROWS")
        
        types = [i.pop(0) for i in data]
        if data_type in self.attendance_commands:
            del types[0]
            del types[-1]
            del data[0]
            del data[-1]
        plot_data = [sum([int(j) for j in data[i]]) for i in range(len(types))]
        loc = './data/images/active_plot.png'
        
        if plot_type in self.plot_pie:
            plt.figure(figsize=(3, 3))
            plt.pie(
                plot_data,
                labels=types,
                autopct='%1.1f%%',
                colors=sns.color_palette('Set2'),
                explode=[0.01 for i in range(len(types))],
                textprops={'fontsize':10}
            )
            plt.title(label="Attendance data for " + exists['name'])
        elif plot_type in self.plot_bar:
            plt.figure(figsize=(5,5))
            plt.bar(
                height=plot_data,
                x=types,
                color='darkviolet'
            )
            plt.title(label="Attendance data for " + exists['name'])
        

        plt.savefig(loc)
        await ctx.send(file=discord.File(loc))

        try:
            os.remove(loc)
        except:
            await dm_error(ctx)


    async def cat(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Please specify [DATA_TYPE SHEET_NAME].")
            return

        data_type = text.pop(0)
        if data_type not in self.attendance_commands and data_type not in self.inventory_commands:
            await ctx.send("Bad data type specification.")
            return
        exists = " ".join(text)
        if exists == None:
            await ctx.send("Please specify a valid sheet name.")
            return

        data = None
        if data_type in self.attendance_commands:
            row_range = "75"
            pull_range = "Attendance!A1:E" + row_range
            data = await self.get_data(ctx, exists['id'], pull_range, dim="COLUMNS")
        elif data_type in self.inventory_commands:
            row_range = "6"
            pull_range = "Inventory!A1:B" + row_range
            data = await self.get_data(ctx, exists['id'], pull_range, dim="ROWS")
        
        types = [i.pop(0) for i in data]
        



    async def list(self, ctx):
        sheet_list = drive.files().list(
            q = f"'{parent}' in parents and trashed=False", orderBy='recency'
        ).execute()

        message = "VTFC data sheets:\n"

        for file in sheet_list.get('files', []):
            message = message + f"- {file['name']}\n"

        await ctx.send(message)


    async def get_link(self, ctx, text, exists):
        spreadsheet_id = exists['id']
        url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'
        embed = discord.Embed()
        embed_image = discord.File('data/images/Google_Sheets_logo.png', filename='sheets_logo.png')
        embed.url = url
        embed.title = " ".join(text)
        embed.description = "The requested Google Sheet."
        embed.set_image(url='attachment://sheets_logo.png')
        await ctx.send(embed=embed, file=embed_image)


class SheetDelete:
    """
    CURRENTLY THERE IS NO CHECK TO SEE IF IT IS ME CALLING THE COMMAND
    """
    async def delete(self, ctx, text):
        text.pop(0)
        if len(text) == 1 or text[len(text) - 1].lower() != "confirm":
            await ctx.send("Please specify a file to delete, and type 'confirm' at the end.")
            return

        text.pop(len(text) - 1)

        exists = find(" ".join(text))
        if exists is None:
            await ctx.send("The file does not exist in the in-use directory.")
            return

        file_id = exists['id']

        drive.files().delete(fileId=file_id).execute()

        await ctx.message.add_reaction(affirmative)



class SheetSet:

    inventory_commands = ["inventory", "i"]
    attendance_commands = ["attendance", "a"]
    epee = ["epee", "e"]
    foil = ["foil", "f"]
    sabre = ["sabre", "saber", "s"]
    attendance_sheet_order = ["date", "foil", "sabre", "epee"]
    inventory_types = ["epee", "e", "foil", "f", "sabre", "saber", "s", "epee bodycord", "ebc",
                       "foil bodycord", "sabre bodycord", "saber bodycord", "rowbc", "maskcord", "mc"]
    #rowbc is right of way bodycord.
    broken = ["broken", "b"]
    fixed = ["fixed", "fi"]
    

    async def eval_next(self, ctx, text):
        del text[0]

        if len(text) == 0:
            await ctx.send("Please specify what you would like to set.")
            return

        if text[0] == "curr":
            await self.curr(ctx, text)
            return
        elif text[0] in self.attendance_commands:
            await self.attendance(ctx, text)
            return
        elif text[0] in self.inventory_commands:
            await self.inventory(ctx, text)
            return

        await ctx.send("Bad command")
    

    async def attendance(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Bad command")
            return
        

        curr_date = str(date.today()) #for results sake
        # if text[0] == "today":
        #     curr_date = date.today()

        for v in [0, 2, 4]:
            if text[v].isnumeric():
                text[v] = int(text[v])
            else:
                await ctx.send("Bad numeric input. Check to see that the format you used is"\
                               " [COUNT WEAPON_NAME]")
                return

        write_data = [curr_date, 0, 0, 0, 0]
        
        duplicate = "You used the same weapon name two or more times. Bad command."

        for w in [1, 3, 5]:
            if text[w] in self.epee:
                if write_data[3] != 0:
                    await ctx.send(duplicate)
                    return
                write_data[3] = text[w - 1]
            elif text[w] in self.sabre:
                if write_data[2] != 0:
                    await ctx.send(duplicate)
                write_data[2] = text[w - 1]
            elif text[w] in self.foil:
                if write_data[1] != 0:
                    await ctx.send(duplicate)
                    return
                write_data[1] = text[w - 1]
            else:
                await ctx.send("Bad weapon entry. Check to see that you spelled everything correctly"\
                               " and that you put it in the order of [COUNT WEAPON_NAME]")
                return
                
        del text[0:6]
        
        exists = find(" ".join(text))
        if exists is None:
            await ctx.send("Bad data location")
            return

        spreadsheet_id = exists['id']

        pull_length = 50 # a little over days of practice for one semester
        pull_range = "Attendance!A1" + ":A" + str(pull_length)

        retrieved_data = await SheetGet().get_data(ctx, spreadsheet_id, pull_range)

        if len(retrieved_data) == pull_length:
            await ctx.send("Consider switching to a new sheet, there are 49 attendance values in this one.")
        
        write_to_range = "Attendance!A" + str(len(retrieved_data) + 1) + ":E" + str(len(retrieved_data) + 1)

        write_data[-1] = sum(write_data[1:4])

        body = {
            'values': [
                write_data
            ]
        }

        try:
            service = build('sheets', 'v4', credentials=credentials)
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, body=body, range=write_to_range, valueInputOption="USER_ENTERED"
            ).execute()
            await ctx.message.add_reaction(affirmative)
        except HttpError as err:
            await dm_error(ctx)


    async def inventory(self, ctx, text):
        """
        !sheet set inventory 1 epee broken Fall 2023
        !sheet set inventory 1 epee bodycord broken Fall 2023
        !sheet set inventory 1 mask cord fixed Fall 2023
        !sheet set inventory 1 maskcord broken Fall 2023
        """

        del text[0] #removes inventory call
        if not len(text) >= 4:
            await ctx.send("Bad command, missing commands.")
            return

        count_to_change = text[0]
        if count_to_change.isnumeric():
            count_to_change = int(count_to_change)
        else:
            await ctx.send("Bad command: immediatly after calling inventory, specify the amount of change as "\
                           "a digit.")
            return
        
        del text[0] #removes the count
        type_to_change = text[0]
        if type_to_change in self.inventory_types and text[1] not in ["body", "bodycord"]:
            del text[0]
        elif text[1] == "bodycord":
            type_to_change = type_to_change + " " + text[1]
            del text[0:2]            
        elif text[2] == "cord":
            type_to_change = type_to_change + " " + "".join(text[1:3])
            del text[0:3]
        else:
            await ctx.send("Bad type specification. If entering a weapon, just specify the type,"\
                           " not the word 'blade'.")
            return

        if type_to_change not in self.inventory_types:
            await ctx.send("Bad type specification. You entered: " + type_to_change + ". Accepted values are: "\
                           + ", ".join(self.inventory_types))
            return

        if text[0] in self.fixed:
            count_to_change *= -1 #depricates the count in the sheet by the amount fixed
        elif text[0] not in self.broken:
            await ctx.send("Bad specification of whether it is broken or fixed.")
            return

        del text[0]

        exists = find(" ".join(text))
        if exists is None:
            await ctx.send("The specified sheet does not exist")
            return

        sheet_row = 1
        if type_to_change in ["foil", "f"]:
            sheet_row = 2
        elif type_to_change in ["sabre", "saber", "s"]:
            sheet_row = 3
        elif type_to_change in ["epee bodycord", "ebc"]:
            sheet_row = 4
        elif type_to_change in ["foil bodycord", "sabre bodycord", "saber bodycord", "rowbc"]:
            sheet_row = 5
        elif type_to_change in ["maskcord", "mc"]:
            sheet_row = 6
        spreadsheet_id = exists['id']
        
        sheet_range = "Inventory!B" + str(sheet_row) + ":B" + str(sheet_row)

        old_data = await SheetGet().get_data(ctx, spreadsheet_id, sheet_range)

        new_data = None
        if len(old_data) == 0:
            new_data = 0 + count_to_change
        else:
            new_data = count_to_change + int(old_data[0][0])

        if new_data < 0:
            new_data == 0

        body = {
            'values':
            [
                [new_data]
            ]
        }

        try:
            service = build('sheets', 'v4', credentials=credentials)
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=sheet_range, body=body, valueInputOption="USER_ENTERED"
            ).execute()
            await ctx.message.add_reaction(affirmative)
        except HttpError as err:
            await dm_error(ctx)
         

    async def curr(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Please specify the name of a sheet you would like to set as in-use.")
            return

        exists = find(" ".join(text))
        if exists is None:
            await ctx.send("There is no sheet by that name within the parent directory.")
            return
        curr = name.split(" ")
        await ctx.message.add_reaction(affirmative)
        

class SheetBuild:

    async def build(self, ctx, text):
        text.pop(0)

        if len(text) == 0 or text[0] != "fencing":
            new_sheet = await self.make_sheet(ctx, text)
            await ctx.message.add_reaction(affirmative)
            return
        elif text[0] == "fencing":
            text.pop(0)
            new_sheet = await self.make_sheet(ctx, text)
            await self.configure_fencing(ctx, new_sheet)
            return


    async def make_sheet(self, ctx, text):
        title = str(date.today())

        if len(text) > 0:
            title = " ".join(text)

        exists = find(title)
        if exists != None:
            await ctx.send("The specified filename already exists. Try using the command 'sheet get list' "\
                           "or choosing a different name.")
            return

        file_metadata = {
            'name': title,
            'parents': [parent],
            'mimeType': 'application/vnd.google-apps.spreadsheet',
        }


        try:
            service = build('sheets', 'v4', credentials=credentials)
            new_sheet = drive.files().create(body=file_metadata).execute()
            return new_sheet
        except HttpError as err:
            await dm_error(ctx)
            return


    async def configure_fencing(self, ctx, new_sheet):
        spreadsheet_id = new_sheet['id']
        
        init_range_att = "Attendance!A1:E1"
        init_values_att = ['Date', 'Foil', 'Sabre', 'Epee', 'Total']
        
        init_range_inv = "Inventory!A1:A6"
        init_values_inv = ['Epee blades', 'Foil blades', 'Sabre blades','Epee bodycords',
                           'Foil/Sabre bodycords', 'Maskcords']
        
        #creates a new sheet named 'Attendance' and renames the first sheet to 'Inventory'
        body_init = {
            'requests':[{
                'addSheet':{
                    'properties':{
                        'title': "Attendance"
                    }
                }
            }, {
                'updateSheetProperties':{
                    'properties':{
                        'sheetId': 0,
                        'title': "Inventory"
                    },
                    'fields': 'title'
                }
            }]
        }
        
        try:
            service = build('sheets', 'v4', credentials=credentials)
            service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body_init).execute()
            response = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        except HttpError as err:
            await dm_error(ctx)
            await ctx.send(err)
            return
        
        body_att = {
            'values':[
                init_values_att
            ]
        }
        body_inv = {
            'majorDimension': 'COLUMNS',
            'values':[
                init_values_inv
            ]
        }
        
        try:
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=init_range_att, body=body_att,
                valueInputOption='USER_ENTERED'
            ).execute()
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=init_range_inv, body=body_inv,
                valueInputOption='USER_ENTERED'
            ).execute()
        except HttpError as err:
            # await dm_error(ctx)
            await ctx.send(err)
            return

        await ctx.message.add_reaction(affirmative)

       
async def setup(bot):
    await bot.add_cog(Sheet(bot))

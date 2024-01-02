import discord
import matplotlib.pyplot as plt
import os
import seaborn as sns
from organize_drive import OrganizeDrive
import alphonse_utils as AlphonseUtils
from alphonse_utils import SheetUtils
from discord.ext import commands
from datetime import date, datetime
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google.oauth2 import service_account
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.errors import HttpError


SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive",
          "https://www.googleapis.com/auth/drive.metadata",
          "https://www.googleapis.com/auth/drive.file"]




#leave all command line here, then make new file for additional shit (rearranging, etc)





SERVICE_ACCOUNT_FILE = "data/sensitive/alphonse-key.json"

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build("drive", "v3", credentials=credentials)

datetime_format = "%Y-%m-%d"


class Sheet(commands.Cog):


    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def flowchart(self, ctx):
        """
        Links to a page describing Alphonse's logic flow for `!sheet`.
        """

        file = discord.File("data/images/will_o_wisp.jpg", filename="wisp.jpg")
        embed = discord.Embed()
        embed.url = "https://github.com/etldrz/alphonse/blob/main/README.md#sheet"
        embed.title = "Flowchart for `!sheet` commands."
        embed.set_image(url="attachment://wisp.jpg")
        await ctx.send(file=file, embed=embed)

    @commands.command()
    async def sheet(self, ctx):
        """
        Command that lets Alphonse know you're dealing with the suite of sheet
        commands. See `!flowchart` for more details.
        """

        text = ctx.message.content.split(" ")
        del text[0]
        if len(text) == 0:
            await ctx.send("Bad command.")
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
                await ctx.send("Bad command. Main command, " + text[0] + ", not valid.")
                return

    
    @commands.command()
    async def att(self, ctx):
        """
        Shortcut for `!sheet set attendance`. Don't specify the sheet name; if for some
        reason you need to specify the name use the extended command.
        """
        
        text = ctx.message.content.split(" ")
        if len(text) == 1:
            await ctx.send("Bad command: you need to input data.")
            return
        text[0] = "attendance"
        if text[-1] in ["epee", "e", "foil", "f", "sabre", "saber", "s"]:
            await SheetSet().check_current_semester(ctx)
            text += SheetUtils.in_use_sheet
            await ctx.send("Using the in-use sheet: " + " ".join(SheetUtils.in_use_sheet))
        await SheetSet().attendance(ctx, text)


    @commands.command()
    async def inv(self, ctx):
        """
        Shortcut for `!sheet set inventory`.
        """
        
        text = ctx.message.content.split(" ")
        text[0] = "inventory"
        if len(text) == 0:
            await ctx.send("Bad command: you need to input data.")
            return
        if text[-1] in ["broken", "b", "fixed", "f"]:
            text = text + SheetUtils.in_use_sheet
            await ctx.send("Using the in-use sheet: " + " ".join(SheetUtils.in_use_sheet))
        await SheetSet().inventory(ctx, text)
    

    @commands.command()
    async def plot(self, ctx):
        """
        Shortcute for `!sheet get plot`.
        """
        text = ctx.message.content.split(" ")
        if len(text) == 1:
            await ctx.send("Bad command: you need to specify what data you want plotted.")
            return
        text[0] = "plot"
        data_types = SheetGet.attendance_commands + SheetGet.inventory_commands
        if text[-1] in data_types:
            text = text + SheetUtils.in_use_sheet
            await ctx.send("Using the in-use sheet: " + " ".join(SheetUtils.in_use_sheet))
        await SheetGet().plot(ctx, text)



class SheetGet:
    """
    DATETIME_FORMATTING: get a/i/in_use_sheet/SHEET_NAME
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
    as_plot = ["plot", "p"]
    plot_pie = ["pie"]
    plot_bar = ["bar"]
    plot_line = ["line"]
                  
    async def eval_next(self, ctx, text):
        """
        Evaluates the next command and redirects to needed function.
        """
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
        elif text[0] == "drive":
            await self.embed_parent_link(ctx)
            return
        
        #If the other options are exhausted, it is assumed that the remainder of the command
        #is a sheet name.
        await self.embed_file_link(ctx, text)
    

    async def get_data(self, ctx, spreadsheet_id, pull_range, dim = "ROWS"):
        """
        Is only good for a single range; if multiple ranges are needed for a single get,
        consider using batchGet. Will pull by rows unless specified otherwise.
        googleapi enums for dim: ROWS COLUMNS
        """
        try:
            service = build("sheets", "v4", credentials=credentials)
            result = service.spreadsheets().values().get(
                spreadsheetId=spreadsheet_id, range=pull_range, majorDimension=dim
            ).execute()
        except HttpError as err:
            await AlphonseUtils.dm_error(ctx)
            return
        data = result.get("values", [])
        return data


    async def plot(self, ctx, text):
        """
        Generates and sends a plot based on commands. The plot is deleted right after use.
        """
        del text[0]
        if len(text) == 0:
            await ctx.send("Please specify [PLOT_TYPE DATA_TYPE SHEET_NAME]")
            return

        plot_type = text[0]
        if plot_type not in self.plot_pie \
           and plot_type not in self.plot_bar \
           and plot_type not in self.plot_line:
            await ctx.send("Please specify PLOT_TYPE more better. Allowed responses are '"\
                           + ", ".join(self.plot_pie) + "' and '" + ", ".join(self.plot_bar) + "'.")
            return
        del text[0]

        data_type = text[0]
        if data_type not in self.attendance_commands \
           and data_type not in self.inventory_commands:
            await ctx.send("Bad specification of data type. Allowed responses are '"\
                           + ", ".join(self.attendance_commands) + "' and '" +\
                           ", ".join(self.inventory_commands) + "'.")
            return
        del text[0]

        if plot_type in self.plot_line \
           and data_type in self.inventory_commands:
            await ctx.send("Line plot is not allowed for inventory.")
            return
        
        exists = SheetUtils.get_file(" ".join(text), drive)
        if exists == None:
            await ctx.send("Please specify a valid sheet name.")
            return

        data = None
        if data_type in self.attendance_commands:
            row_range = "75"
            pull_range = "Attendance!A1:E" + row_range
            data = await self.get_data(ctx, exists["id"], pull_range, "COLUMNS")
        elif data_type in self.inventory_commands:
            row_range = "6"
            pull_range = "Inventory!A1:B" + row_range
            data = await self.get_data(ctx, exists["id"], pull_range, "ROWS")
        
        loc = "code/data/images/active_plot.png"
        
        if plot_type in self.plot_pie:
            types = [i.pop(0) for i in data]            
            if data_type in self.attendance_commands:
                del types[0]
                del types[-1]
                del data[0]
                del data[-1]

            plot_data = [sum([int(j) for j in data[i]]) for i in range(len(types))]
                
            plt.figure(figsize=(3, 3))
            plt.pie(
                plot_data,
                labels=types,
                autopct="%1.1f%%",
                colors=sns.color_palette("Set2"),
                explode=[0.01 for i in range(len(types))],
                textprops={"fontsize":10}
            )
            if data_type in self.attendance_commands:
                plt.title(label="Attendance for " + exists["name"])
            elif data_type in self.inventory_commands:
                plt.title(label="Broken inventory for " + exists["name"])
        elif plot_type in self.plot_bar:
            types = [i.pop(0) for i in data]            
            if data_type in self.attendance_commands:
                del types[0]
                del types[-1]
                del data[0]
                del data[-1]

            plot_data = [sum([int(j) for j in data[i]]) for i in range(len(types))]
                
            plt.figure(figsize=(7, 5))
            plt.bar(
                height=plot_data,
                x=types,
                color="steelblue"
            )
            if data_type in self.attendance_commands:
                plt.title(label="Attendance for " + exists["name"])
            elif data_type in self.inventory_commands:
                plt.title(label="Broken inventory for " + exists["name"])
            plt.xticks(rotation=12, ha="right")
        elif plot_type in self.plot_line:
            [i.pop(0) for i in data]
            dates = [i.strftime("%b-%d") \
                     for i in [datetime.strptime(j, datetime_format) \
                               for j in data[0]]]
            step_size = int(len(dates) / 3)
            total_att = [int(i) for i in data[-1]]
            plt.figure(figsize=(7,5))
            plt.plot(dates, total_att)
            plt.title(label="Nightly attendance for " + exists["name"])
            plt.xlabel(None)
            plt.ylabel("attendance")
            plt.xticks([dates[0], dates[step_size*1], dates[step_size*2], dates[-1]])


        plt.savefig(loc)
        await ctx.send(file=discord.File(loc))

        try:
            os.remove(loc)
        except:
            await AlphonseUtils.dm_error(ctx)


    async def list(self, ctx):
        """
        Sends a list of sheets within the parent directory to the chat.
        """
        
        sheet_list = drive.files().list(
            q = f"'{SheetUtils.parent}' in parents and trashed=False", orderBy="recency"
        ).execute()

        message_sheets = "Spreadsheets directly within parent folder:\n"
        message_folders = "Sub-directories:\n"
        for file in sheet_list.get("files", []):
            if file["mimeType"] == SheetUtils.folder_mimetype:
                message_folders += f"- {file['name']}\n"
            else:
                if file["name"] == " ".join(SheetUtils.in_use_sheet):
                    message_sheets += f"- **{file['name']}**\n"
                else:
                    message_sheets += f"- {file['name']}\n"

        await ctx.send(message_sheets + message_folders)


    async def embed_file_link(self, ctx, text):
        """
        Sends a link of the named sheet or folder to the chat.
        """
        
        exists = SheetUtils.get_file(" ".join(text), drive)
        if exists == None:
            message = "I'm not seeing the requested sheet/folder." \
                " It be that you misspelled the request, or that" \
                " it doesn't exist. Try `!sheet get drive`"
            await ctx.send(message)
            return

        spreadsheet_id = exists["id"]
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}"
        #This accounts for the what-if of a folder being searched for
        if exists["mimeType"] == SheetUtils.folder_mimetype: 
            url = "https://drive.google.com/drive/u/0/folders/" + exists["id"]
        embed = discord.Embed()
        embed_image = discord.File("data/images/Google_Sheets_logo.png", filename="sheets_logo.png")
        embed.url = url
        embed.title = exists["name"]
        embed.description = "The requested item."
        embed.set_image(url="attachment://sheets_logo.png")
        await ctx.send(embed=embed, file=embed_image)


    async def embed_parent_link(self, ctx):
        """
        Links to the parent Google Drive folder.
        """
        
        file = discord.File("data/images/oppie_uppies.jpg", filename="oppie_uppies.jpg")
        embed = discord.Embed()
        embed.url = "https://drive.google.com/drive/u/0/folders/" + SheetUtils.parent
        embed.title = "VTFC Data -- Google Drive"
        embed.set_image(url="attachment://oppie_uppies.jpg")
        await ctx.send(file=file, embed=embed)
 

class SheetDelete:


    async def delete(self, ctx, text):
        """
        Deletes the named sheet.
        """
        
        if not AlphonseUtils.check_if_personal(ctx):
            await ctx.send("You don't have the required permission for that action.")
            return

        del text[0]
        if len(text) == 0 or text[-1].lower() != "confirm":
            await ctx.send("Please specify a file to delete, and type 'confirm' at the end.")
            return

        del text[-1]
        exists = SheetUtils.get_file(" ".join(text), drive)
        if exists is None:
            await ctx.send("The file does not exist in the in-use directory.")
            return

        if exists["mimeType"] == SheetUtils.folder_mimetype:
            message = "You have requested to delete a folder " \
                "within the parent directory. Due to an excess " \
                "of caution, please delete it manually. Try `!sheet get drive`."
            await ctx.send(message)
            return
        
        file_id = exists["id"]
        updated_body = {"trashed": True}
        drive.files().update(fileId=file_id, body=updated_body).execute()
        await AlphonseUtils.affirmation(ctx)


class SheetSet:

    inventory_commands = ["inventory", "i"]
    attendance_commands = ["attendance", "a"]
    epee = ["epee", "e"]
    foil = ["foil", "f"]
    sabre = ["sabre", "saber", "s"]
    attendance_sheet_order = ["date", "foil", "sabre", "epee"]
    inventory_types = ["epee", "e", "foil", "f", "sabre", "saber", "s",
                       "epee bodycord", "ebc", "foil bodycord",
                       "sabre bodycord", "saber bodycord", "rowbc", 
                       "maskcord", "mc"]
    broken = ["broken", "b"]
    fixed = ["fixed", "fi"]
    

    async def eval_next(self, ctx, text):
        """
        Redirects the logic to the next named command.
        """
        
        del text[0]

        if len(text) == 0:
            await ctx.send("Please specify what you would like to set.")
            return

        if text[0] == SheetUtils.user_keyword_in_use_sheet:
            await self.set_in_use_sheet(ctx, text)
            return
        elif text[0] in self.attendance_commands:
            await self.attendance(ctx, text)
            return
        elif text[0] in self.inventory_commands:
            await self.inventory(ctx, text)
            return

        await ctx.send("Bad command")
    

    async def attendance(self, ctx, text):
        """
        Sets the weapon attendance for the named sheet.
        """
        
        del text[0]
        if len(text) == 0 or len(text) < 6:
            await ctx.send("Bad command due to length.")
            return

        current_date = str(date.today())

        #This loop checks to see that the inputted attendance ints are all there.
        for v in [0, 2, 4]:
            if text[v].isnumeric():
                text[v] = int(text[v])
            else:
                message = "Bad numeric input. Check to see that the datetime_format you used is" \
                    " [COUNT WEAPON_NAME]x3"
                await ctx.send()
                return

        #What will eventually be put into the sheet.
        write_data = [current_date, 0, 0, 0, 0]
        
        #This loop checks to see that each weapon is inputted only once, as well as being valid
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
                message = "Bad weapon entry. Check to see that you spelled everything correctly" \
                    " and that you put it in the order of [COUNT WEAPON_NAME]"
                await ctx.send(message)
                return

        del text[0:6]
        name = " ".join(text)
        exists = SheetUtils.get_file(name, drive)
        if exists is None:
            await ctx.send("Bad sheet name.")
            return
        spreadsheet_id = exists["id"]

        #Google API doesn't populate the returned list with empty cells,
        #hence the initial range pull acting as the write_to_range length
        pull_length = 75 #Well over how many days of practice are in one semester

        pull_range = "Attendance!A1" + \
            ":A" + \
            str(pull_length)

        retrieved_data = await SheetGet().get_data(ctx, spreadsheet_id, pull_range)

        write_to_range = "Attendance!A" + \
            str(len(retrieved_data) + 1) + \
            ":E" + \
            str(len(retrieved_data) + 1)

        write_data[-1] = sum(write_data[1:4])

        await self.add_data_single_range(ctx, spreadsheet_id, write_data, write_to_range)


    async def inventory(self, ctx, text):
        """
        !sheet set inventory 1 epee broken Fall 2023
        !sheet set inventory 1 epee bodycord broken Fall 2023
        !sheet set inventory 1 mask cord fixed Fall 2023
        !sheet set inventory 1 maskcord broken Fall 2023
        """

        del text[0] 
        if not len(text) >= 4:
            await ctx.send("Bad command, missing commands.")
            return

        count_to_change = text[0]
        if count_to_change.isnumeric():
            count_to_change = int(count_to_change)
        else:
            message = "Bad command: immediatly after calling inventory, "\
                "specify the amount of change as a digit."
            await ctx.send(message)
            return
        
        del text[0]
        type_to_change = text[0]

        if type_to_change in self.inventory_types and \
           text[1] not in ["body", "bodycord"]:
            del text[0]
        elif text[1] == "bodycord":
            type_to_change = type_to_change + " " + text[1]
            del text[0:2]            
        elif text[2] == "cord":
            type_to_change = type_to_change + " " + "".join(text[1:3])
            del text[0:3]
        else:
            message = "Bad type specification. If entering a weapon, "\
                "just specify the type, not the word 'blade'."
            await ctx.send(message)
            return

        if type_to_change not in self.inventory_types:
            message = "Bad type specification. You entered: " + \
                type_to_change + ". Accepted values are: " + \
                ", ".join(self.inventory_types)
            await ctx.send(message)
            return

        if text[0] in self.fixed:
            count_to_change *= -1
        elif text[0] not in self.broken:
            message = "Bad specification of whether it is broken or fixed."
            await ctx.send(message)
            return

        del text[0]

        exists = SheetUtils.get_file(" ".join(text), drive)
        if exists is None:
            message = "The specified sheet does not exist"
            await ctx.send(message)
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
        spreadsheet_id = exists["id"]
        
        write_to_range = "Inventory!B" + str(sheet_row) + ":B" + str(sheet_row)

        old_data = await SheetGet().get_data(ctx, spreadsheet_id, sheet_range)

        new_data = None
        if len(old_data) == 0:
            new_data = 0 + count_to_change
        else:
            new_data = count_to_change + int(old_data[0][0])

        if new_data < 0:
            new_data == 0

        self.add_data_single_range(spreadsheet_id, new_data, write_to_range)


    async def set_in_use_sheet(self, ctx, text):
        del text[0]
        if len(text) == 0:
            await ctx.send("Please specify the name of a sheet you would like to set as in-use.")
            return

        exists = SheetUtils.get_file(" ".join(text), drive)
        if exists is None:
            await ctx.send("There is no sheet by that name within the directory.")
            return
        elif exists["mimeType"] == SheetUtils.folder_mimetype:
            await ctx.send("You cannot select a folder to be the in-use sheet.")
            return
        SheetUtils.in_use_sheet = exists["name"].split(" ")
        await AlphonseUtils.affirmation(ctx)


    async def check_current_semester(self, ctx):
        """
        Checks to see if the correct sheet is being used for data input, based on when the command
        is called. If the incorrect sheet is being used, the in-use sheet is set to be the
        current semester/year and a sheet with this name is created if it doesn't already exist.
        """

        correct_name = SheetBuild().make_fencing_sheet_name(for_semester=True)
        if correct_name != SheetUtils.in_use_sheet:
            message = "Looks like you're calling a data-input command into a " \
                "sheet which does not correspond to the current semester and/or " \
                "year. The in-use sheet will be changed to " + " ".join(correct_name) + \
                " and a new sheet with that name will be created if one doesn't " \
                "already exist.\n\nYou don't have to do anything else."
            await ctx.send(message)

            #If the call is being made at the start of Fall semester, combine
            #last years two sheets into one and place all three sheets into a sub-directory.
            if AlphonseUtils.is_fall_semester():
                await OrganizeDrive().combine_semesters(ctx)
            SheetUtils.in_use_sheet = correct_name
            exists = SheetUtils.get_file(" ".join(SheetUtils.in_use_sheet, drive))
            if exists is None:
                #The list being added to is because build() expects a command.
                await SheetBuild().build(ctx, [""] + correct_name)
        return correct_name


    async def add_data_single_range(self, ctx, spreadsheet_id, data_values, write_to_range):
        """
        Writes the inputted data to the inputted range on the inputted sheet.
        """
        body = {
            "values": [
                data_values
            ]
        }

        try:
            service = build("sheets", "v4", credentials=credentials)
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, body=body,
                range=write_to_range, valueInputOption="USER_ENTERED"
            ).execute()

            await AlphonseUtils.affirmation(ctx)
        except HttpError as err:
            message = "The data was unabled to be added :: "\
                "SheetSet.add_data_single_range()\n" \
                "The given error is " + str(err) + "\n"
            await AlphonseUtils.dm_error(ctx, message)


#    async def add_data_batch_update(self, ctx, spreadsheet_id, data_values, write_to_range):
#        body = {
#            "requests":[
#                {
#                    "insertDimension": {
#                        "range": {
#                            "sheetId": spreadsheet_id,
#                            "dimension": dim,
#                            "startIndex": start_index,
#                            "endIndex": end_index
#                        },
#                        "inheritFromBefore": True:
#                    }
#                }
#            ]
#        }
         

class SheetBuild:


    def make_fencing_sheet_name(self, for_semester):
        """
        for_semester is a bool representing if the name is for one semester or the whole year.
        The name returned is created accordingly. Only used internally, not directly via
        user commands.
        """
        current_name = str(date.today().year - 1) + "-" + str(date.today().year)
        if for_semester:
            current_name = SheetUtils.semester_fall if AlphonseUtils.is_fall_semester() \
                else SheetUtils.semester_spring
            current_name += " " + str(date.today().year)
        return current_name.split(" ")
        
        
    async def build(self, ctx, text):
        """
        Builds a sheet with the given name specifically for VTFC use.
        No inputted name means that the date it was called is used as the sheet name.
        """

        del text[0]

        new_sheet = await self.make_sheet(ctx, text)
        await self.configure_fencing(ctx, new_sheet)
        return


    async def make_sheet(self, ctx, text):
        """
        Makes a sheet via GoogleSheets.api. With no specified name,
        the sheet name is the date that it was created.
        """
        
        title = str(date.today())
        if len(text) > 0:
            title = " ".join(text)

        exists = SheetUtils.get_file(title, drive)
        if exists != None:
            message = "The specified filename already exists. Try using the command " \
                "`!sheet get list` or choosing a different filename."
            await ctx.send(message)
            return

        file_metadata = {
            "name": title,
            "parents": [SheetUtils.parent],
            "mimeType": "application/vnd.google-apps.spreadsheet",
        }

        try:
            service = build("sheets", "v4", credentials=credentials)
            new_sheet = drive.files().create(body=file_metadata).execute()
            return new_sheet
        except HttpError as err:
            await AlphonseUtils.dm_error(ctx)
            return


    async def configure_fencing(self, ctx, new_sheet):
        """
        Configures the sheet to be for fencing.
        """
        
        spreadsheet_id = new_sheet["id"]
        
        init_range_att = "Attendance!A1:E1"
        init_values_att = ["Date", "Foil", "Sabre", "Epee", "Total"]
        
        init_range_inv = "Inventory!A1:A6"
        init_values_inv = ["Epee blades", "Foil blades", "Sabre blades","Epee bodycords",
                           "Foil/Sabre bodycords", "Maskcords"]
        
        #Creates a new sheet named "Attendance" and renames the first sheet to "Inventory"
        body_init = {
            "requests":[{
                "addSheet":{
                    "properties":{
                        "title": "Attendance"
                    }
                }
            }, {
                "updateSheetProperties":{
                    "properties":{
                        "sheetId": 0,
                        "title": "Inventory"
                    },
                    "fields": "title"
                }
            }]
        }
        
        try:
            service = build("sheets", "v4", credentials=credentials)
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body_init).execute()
            
            response = service.spreadsheets().get(
                spreadsheetId=spreadsheet_id).execute()
        except HttpError as err:
            await AlphonseUtils.dm_error(ctx)
            return
        
        body_att = {
            "values":[
                init_values_att
            ]
        }
        body_inv = {
            "majorDimension": "COLUMNS",
            "values":[
                init_values_inv
            ]
        }
        
        try:
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=init_range_att, body=body_att,
                valueInputOption="USER_ENTERED"
            ).execute()

            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, range=init_range_inv, body=body_inv,
                valueInputOption="USER_ENTERED"
            ).execute()
        except HttpError as err:
            await AlphonseUtils.dm_error(ctx)
            return

        await AlphonseUtils.affirmation(ctx)

       
async def setup(bot):
    await bot.add_cog(Sheet(bot))

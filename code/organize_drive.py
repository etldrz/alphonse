import alphonse_utils as AlphonseUtils
from alphonse_utils import SheetUtils
from datetime import date
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


SERVICE_ACCOUNT_FILE = "data/sensitive/alphonse-key.json"

credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build("drive", "v3", credentials=credentials)



class OrganizeDrive():
    

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


    async def check_correct_sheet(self, ctx):
    """
    Checks to see if the correct sheet is being used for data input, based on when the command
    is called. If the incorrect sheet is being used, the in-use sheet is set to be the
    current semester/year and a sheet with this name is created if it doesn't already exist.
    """

    exists =  None
    correct_name = self.make_fencing_sheet_name(for_semester=True)
    if correct_name != SheetUtils().in_use_sheet:
        message = "Looks like you're calling a data-input command into a " \
            "sheet which does not correspond to the current semester and/or " \
            "year. The in-use sheet will be changed to " + " ".join(correct_name) + \
            " and a new sheet with that name will be created if one doesn't " \
            "already exist.\n\nYou don't have to do anything else. If you wish to " \
            "bypass this assumption, use the full command: `!sheet set attendance VALUES`."
        await ctx.send(message)

        #If the call is being made at the start of Fall semester, combine
        #last years two sheets into one and place all three sheets into a sub-directory.
        if AlphonseUtils.is_fall_semester():
            await self.combine_semesters(ctx)
        SheetUtils().in_use_sheet = correct_name
        exists = SheetUtils().get_file(" ".join(SheetUtils().in_use_sheet, drive))
    return exists


    async def combine_semesters(self, ctx):
        """
        Only works for attendance right now.
        """

        #year_range = [str(date.today().year - 1), str(date.today().year)]
        year_range = ["2021", "2022"]
        current_fall_file = SheetUtils().get_file(Sheet.semester_fall + " " + year_range[0])
        current_spring_file = SheetUtils().get_file(Sheet.semester_spring + " " + year_range[1])

        if current_fall_file is None or current_spring_file is None:
            message = "One or both of the data sheets for the year range " \
                "'" + "-".join(year_range) + "' could not be found. " \
                "\nCalled from alphonse_utils.OrganizeDrive.combine_semesters()"
            SheetUtils().dm_error(ctx, message)
            return

        #this range is well more than the amount of practices per semester.
        row_range = "75"
        pull_range = "Attendance!A2:E" + row_range
        combined_name = "Data " + "-".join(year_range)

        try:
            fall_attendance = await SheetGet().get_data(
                ctx, current_fall_file["id"], pull_range, "COLUMNS")
            spring_attendance = await SheetGet().get_data(
                ctx, current_spring_file["id"], pull_range, "COLUMNS")
        except:
            AlphonseUtils.dm_error(ctx)

        combined_data = [i + j for i, j in zip(fall_attendance, spring_attendance)]
        await ctx.send(combined_data)
        await SheetBuild().build(ctx, [""] + ["fencing"] + [combined_name])
        combined = get_file(combined_name)
        push_range = "Attendance!A2:E" + str(len(combined_data[0]) + 1)
        await ctx.send(push_range)
        await SheetSet().add_data_single_range(
            ctx, combined["id"], combined_data, push_range)

        new_folder = await self.create_folder(ctx)
        if new_folder is None:
            return
        
        parent_id = new_folder["id"]
        await self.move_file(ctx, current_fall_file, parent_id)
        await self.move_file(ctx, current_spring_file, parent_id)
        await self.move_file(ctx, combined, parent_id)
        await AlphonseUtils.affirmation(ctx)


    async def create_folder(self, ctx):
        folder_name = str(date.today().year - 1) + "-" + str(date.today().year)
        try:
            service = build("drive", "v3", credentials=credentials)
            file_metadata = {
                "name": folder_name,
                "mimeType": folder_mimetype,
                "parents": [parent]
            }

            file = service.files().create(body=file_metadata, fields="id").execute()
            return file
        except HttpError as error:
            await AlphonseUtils.dm_error(ctx)
            return None


    async def move_file(self, ctx, file_to_move, new_parent_id):
        file_id = file_to_move["id"]

        try:
            service = build("drive", "v3", credentials=credentials)
            file = service.files().get(fileId=file_id, fields="parents").execute()
            previous_parents = ",".join(file.get("parents", []))
            file = (
                service.files()
                .update(
                    fileId=file_id,
                    addParents=new_parent_id,
                    removeParents=previous_parents,
                    fields="id, parents",
                )
            ).execute()
        except HttpError as error:
            await ctx.dm_error(ctx)



class PopulateDrive:


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
 

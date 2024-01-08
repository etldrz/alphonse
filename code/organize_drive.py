import alphonse_utils as AlphonseUtils
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


SERVICE_ACCOUNT_FILE = "data/sensitive/alphonse-key.json"

creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
drive = build("drive", "v3", credentials=creds)



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

        exists = None
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
            #if AlphonseUtils.is_fall_semester():
            if True:
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
        current_fall_file = SheetUtils().get_file(
            SheetUtils().semester_fall + " " + year_range[0], drive)
        current_spring_file = SheetUtils().get_file(
            SheetUtils().semester_spring + " " + year_range[1], drive)

        if current_fall_file is None or current_spring_file is None:
            message = "One or both of the data sheets for the year range " \
                "'" + "-".join(year_range) + "' could not be found. " \
                "\nCalled from alphonse_utils.OrganizeDrive.combine_semesters()"
            SheetUtils().dm_error(ctx, message)
            return
        await ctx.send("we got to 88")

        #this range is well more than the amount of practices per semester.
        row_range = "75"
        pull_range = "Attendance!A2:E" + row_range
        combined_name = "Data " + "-".join(year_range)

        try:
            fall_attendance = await PopulateDrive().get_data(
                ctx, current_fall_file["id"], pull_range, "COLUMNS")
            spring_attendance = await PopulateDrive().get_data(
                ctx, current_spring_file["id"], pull_range, "COLUMNS")
        except:
            AlphonseUtils.dm_error(ctx)

        await ctx.send("we got to 103")

        combined_data = [i + j for i, j in zip(fall_attendance, spring_attendance)]
        await ctx.send(combined_data)
        #The build call expects a verbal command, hence the list
        await SheetBuild().build(ctx, [""] + [combined_name])
        combined = get_file(combined_name)
        push_range = "Attendance!A2:E" + str(len(combined_data[0]) + 1)
        await ctx.send(push_range)
        await PopulateDrive().add_data_batch(
            ctx, combined["id"], combined_data, push_range, "ROWS")

        await ctx.send("we got past the batch")

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
            service = build("drive", "v3", credentials=creds)
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
            service = build("drive", "v3", credentials=creds)
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


    def get_service(self):
        return build("sheets", "v4", credentials=creds)


    async def get_data(self, ctx, spreadsheet_id, pull_range, dim = "ROWS"):
        """
        Is only good for a single range; if multiple ranges are needed for a single get,
        consider using batchGet. Will pull by rows unless specified otherwise.
        googleapi enums for dim: ROWS COLUMNS
        """
        try:
            service = self.get_service()
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
            service = self.get_service()
            service.spreadsheets().values().update(
                spreadsheetId=spreadsheet_id, body=body,
                range=write_to_range, valueInputOption="RAW"
            ).execute()

            await AlphonseUtils.affirmation(ctx)
        except HttpError as err:
            message = "The data was unabled to be added :: "\
                "SheetSet.add_data_single_range()\n" \
                "The given error is " + str(err) + "\n"
            await AlphonseUtils.dm_error(ctx, message)


    async def add_data_batch(self, ctx, spreadsheet_id, data_values, write_to_range,
                             major_dimension):
        value_range = {
            "range": write_to_range,
            "majorDimension": major_dimension,
            "values":[data]
        }
        body = {
            "valueInputOption": "RAW",
            "data": [
                {
                    value_range
                }
            ]
        }

        try:
            service = self.service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id, body=body
            ).execute()
        except HttpError as error:
            AlphonseUtils().dm_error(error)

        

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
    if not AlphonseUtils.is_fall_semester(): 
        current_sheet = semester_spring
    in_use_sheet = [current_sheet, str(datetime.today().year)] 



    def get_file(self, name, drive):
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

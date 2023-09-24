import discord
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

curr_sheet = None # holds the name of the current working sheet

affirmative = '\U0001F44D' #Al's reaction to a message when the job is completed successfully.


def find(name):
    sheet_list = drive.files().list(q=f"'{parent}' in parents and trashed=False").execute()

    for file in sheet_list.get('files', []):
        if file['name'] == name:
            return file

    return None


async def dm_error():
    await ctx.send("uh oh")


class SheetGet:

    async def eval_next(self, bot, ctx, text):
        if len(text) == 0:
            await ctx.send("Please further speciffy what you want.")
            return

        text.pop(0)
        if text[0] == "list":
            await self.list(bot, ctx)
            return
    
        exists = None
        if text[0] == "curr":
            exists = find(curr_sheet)
            text = curr_sheet
        else:
            exists = find(" ".join(text))
        if exists == None:
            await ctx.send("The specified file does not exist.")
            return

        await self.get(bot, ctx, text, exists)


    async def list(self, bot, ctx):
        sheet_list = drive.files().list(q= f"'{parent}' in parents and trashed=False", orderBy='recency').execute()

        message = "VTFC data sheets:\n"

        for file in sheet_list.get('files', []):
            message = message + f"- {file['name']}\n"

        await ctx.send(message)


    async def get(self, bot, ctx, text, exists):
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
    
    async def delete(self, ctx, text):
        text.pop(0)
        if len(text) == 1 or text[len(text) - 1].lower() != "confirm":
            await ctx.send("Please specify a file to delete, and type 'confirm' at the end.")
            return

        text.pop(len(text) - 1)

        exists = find(" ".join(text))
        if exists == None:
            await ctx.send("The file does not exist in the in-use directory.")
            return

        file_id = exists['id']

        drive.files().delete(fileId=file_id).execute()

        await ctx.message.add_reaction(affirmative)



class SheetSet:

    async def eval_next(self, ctx, text):
        text.pop(0)

        if len(text) == 0:
            await ctx.send("Please specify what you would like to set.")
        
    
    async def attendance():
        return

    async def inventory():
        return

    async def curr():
        return



class SheetBuild:

    async def build(self, ctx, text):
        text.pop(0)

        if len(text) == 0 or text[0] != "fencing":
            new_sheet = self.make_sheet(ctx, text)
            await ctx.message.add_reaction(affirmative)
            return
        elif text[0] == "fencing":
            text.pop(0)
            new_sheet = await self.make_sheet(ctx, text)
            await self.build_fencing(ctx, new_sheet)
            return


    async def make_sheet(self, ctx, text):
        title = str(date.today())

        if len(text) > 0:
            title = " ".join(text)

        exists = find(title)
        if exists != None:
            await ctx.send("The specified filename already exists. Try using the command 'sheet get list'"\
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


    async def build_fencing(self, ctx, new_sheet):
        spreadsheet_id = new_sheet['id']
        
        init_range_att = "Attendance!A1:E1"
        init_values_att = ['Date', 'Foil', 'Sabre', 'Epee', 'Total']
        
        init_range_inv = "Broken_Count!A1:C1"
        init_values_inv = ['Foil', 'Sabre', 'Epee']
        
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
                        'title': "Broken_Count"
                    },
                    'fields': 'title'
                }
            }]
        }
        
        service = build('sheets', 'v4', credentials=credentials)

        service.spreadsheets().batchUpdate(spreadsheetId=spreadsheet_id, body=body_init).execute()
        response = service.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()
        sheet_ids = response.get('sheets', '')
        
        body_att = {
            'values':[
                init_values_att
            ]
        }

        body_inv = {
            'values':[
                init_values_inv
            ]
        }
        
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=init_range_att, body=body_att, valueInputOption='USER_ENTERED'
        ).execute()
        service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=init_range_inv, body=body_inv, valueInputOption='USER_ENTERED'
        ).execute()

        await ctx.message.add_reaction(affirmative)

       



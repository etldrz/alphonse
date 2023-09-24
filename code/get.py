class SheetGet:
    def __init__(self, bot, drive, discord, personal_id, ctx, text):
        self.bot = bot
        self.ctx = ctx
        text.pop(0) #removing the 'get' keyword
        self.text = text


    async def eval_next(self):
        if len(text) == 0:
            await ctx.send("Please further speciffy what you want.")
            return

        if text[0] == "list":
            await self.sheet_list(ctx)
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


    async def sheet_list(ctx):
        sheet_list = drive.files().list(q= f"'{parent}' in parents and trashed=False", orderBy='recency').execute()

        message = "VTFC data sheets:\n"
        try:
            for file in sheet_list.get('files', []):
                message = message + f"- {file['name']}\n"
                await ctx.send(message)
        except:
            user = bot.get_user(personal_id)
            await user.send(f"A problem occured with the command '{ctx.message.content}'")


    async def sheet_get(ctx, text):
    try:
        spreadsheet_id = exists['id']
        url = f'https://docs.google.com/spreadsheets/d/{spreadsheet_id}'

        embed = discord.Embed()
        embed_image = discord.File('Google_Sheets_logo.png', filename='sheets_logo.png')
        embed.url = url
        embed.title = " ".join(text)
        embed.description = "The requested Google Sheet."
        embed.set_image(url='attachment://sheets_logo.png')
        await ctx.send(embed=embed, file=embed_image)
    except:
        user = bot.get_user(personal_id)
        await user.send(f"A problem occured with the command '{ctx.message.content}'")

        


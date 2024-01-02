class OrganizeDrive():
    

    async def combine_semesters(self, ctx):
        """
        Only works for attendance right now.
        """

        #year_range = [str(date.today().year - 1), str(date.today().year)]
        year_range = ["2021", "2022"]
        current_fall_file = get_file(Sheet.semester_fall + " " + year_range[0])
        current_spring_file = get_file(Sheet.semester_spring + " " + year_range[1])

        if current_fall_file is None or current_spring_file is None:
            message = "One or both of the data sheets for the year range " \
                "'" + "-".join(year_range) + "' could not be found. " \
                "\nCalled from alphonse_utils.OrganizeDrive.combine_semesters()"
            dm_error(ctx, message)
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
        await SheetSet().add_data_single_range(ctx, combined["id"], combined_data, push_range)

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



# A man walks down the street<br>it's a street in a strange world

## TODO:
- move sensitive info out of the main.py
- make it so that quote.submit will record responses. if it does record a response, credit the quote to the original message
- Make Al post rules that go along with most.dangerous.game when it is called. Make sub-commands (or external link) so that people can see their own scores.
- Make a command accessible only by me that will kill every active process.
- Make sheet.build with no name not get too specific with the time
- Make the date input more better for SheetBuild.attendance. Also make shortcut methods !broke and !atten, as well as a way to rollback the data (if date is the same use only the most previous)


## Commands:

Every command is prefecaed by '!'. Information on each command can be found inside Discord by typing '!help COMMAND_NAME'

### `mood`

mood will generate a randomly chosen emote from the list of emotes specific to the server the command is called on.

### `most.dangerous.game` (VTFC specific)

Runs a contest among all members in the server. Whenever someone posts an image into the 'fencer-spotted' channel, a point will be awarded to them. At the end of the contest, Alphonse will announce the winner of the contest.

Takes a potential input representing the amount of hours the contest will run for. If no number is given, the runtime will be 48.

### `quote`

quote will return a randomly selected quote from a database that Al has access to.

### `quote.submit`

Takes a line of text as a parameter, that text will be logged for review to submission to the file that `quote` uses. The name of the user who submitted it will be saved as well.

### `remind.me`

Takes a date and text that the user would like to be reminded of. On the specified date at 9am, Alphonse will post the reminder and ping the user in the channel the command was originally called in.

FORMAT: 'MM/DD/YYYY USER_TEXT'

### 'sheet'

The 'sheet' command is used to interface with GoogleSheets directly from Discord. The general format it follows is '!sheet ACTION ACTION_SPECIFICS'. All sheets Alphonse has access to are in a specific parent folder inside Evan's GoogleDrive. The main actions are as follows:
- 'build' This creates a new sheet with a user specified name. Optional: specifying 'fencing' before the name tells Alphonse to build a sheet formatted for VTFC data collection purposes (having tabs for inventory and for fencing, and prefilled squares). Several commands can only be used with this fencing format.
  - Example call: '!sheet build fencing Spring 2024'
- 'get' This gets specified data and returns it to the user.
  - 'list' This has Alphonse send a list of the current sheets inside the parent folder to the channel from which the command was called.
  - 'plot' This has Alphonse send a plot of the specified data. Only works for sheets build with fencing, or formatted respectively.
    - 'bar/pie/line' Choosing one of these options generates a barchar, piechart, and line plot respectively. Line plots cannot be called for 'inventory'.
      - 'attendance/inventory' Data type for the plot.
        - 'SHEET_NAME' Location of the data.
  - 'SHEET_NAME' Returns an embeded link of the specified sheet.
- 'set' Allows the caller to change data.
  - 'curr' Sets a shortcut for a sheet commonly in use.
    - 'SHEET_NAME' The sheet name you would like to assign to 'curr'
  - 'attendance' Sets attendance for the date the command was called on
    - '# WEAPON_NAME'x3 Inputted values for the numbers attending practice.
      - 'SHEET_NAME' The sheet you want the attendance to be saved to.
  - 'inventory' Sets inventory data
    - '# ITEM_NAME'x1 The item you want to mark as broken or fixed.
      - 'broken/fixed' If broken is specified, the specified number is added to the value in the sheet. If fixed, that number is removed from the value in the sheet.
        - 'SHEET_NAME'
- 'delete' Deletes the specified sheet.
  - 'SHEET_NAME'
    - 'confirm' Without adding this to the end, the sheet won't be deleted.
- For ease, commands commonly called have been given shortcuts. Shortcuts do not need !sheet in front of them. If a shortcutted command takes normally 'SHEET_NAME' at the end, leaving it off here will just apply the command to the in-use sheet (set by '!sheet set curr SHEET_NAME')
  - '!plot' Takes the same values as the long version of '!sheet get plot'
  - '!inv' Takes the same values as the long version of '!sheet set inventory'
  - '!att' Takes the same values as the long version of '!sheet set attendance'

**EXAMPLE COMMANDS:**

'!sheet build fencing Fall 2023'

'!sheet set curr Fall 2023'

'!att 10 epee 9 foil 12 sabre' (alternatively: '!att 10 e 9 f 12 s')

'!inv 3 foil body cord broken' (alternatively: '!inv 3 rowbc broken', where 'rowbc' is short for right-of-way bodycord)

'!sheet get list'

'!sheet delete test confirm'

'!plot pie attendance' (alternatively: '!plot pie a')

'!sheet delete Fall 2023 confirm'



### `source`

Reterns an embedded link to Alphonse's GitHub homepage (here!).



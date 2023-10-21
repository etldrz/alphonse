# [A man walks down the street<br>it's a street in a strange world](https://www.youtube.com/watch?v=OMbfT3Wppjo)

# Commands:

Every command is prefecaed by '!'. Information on each command can be found inside Discord by typing '!help COMMAND_NAME'

## `MostDangerousGame`

This set of commands revolves around a contest for the VTFC Discord channel #fencer-spotted. Once the contest begins, guild members can accrue points by posting images into #fencer-spotted; once the contest is over the winner and runners up will be announced.

- ### `friendship.killer`

To be immediatly followed by a time length (in hours) that the contest will run for. Only opperates in a specific channel, initially #fencer-spotted, but can be altered by the command immediatly below.

- ### `change.server`
  
When immediatly followed by a valid server name within the guild where the command is being called, that server will become the new arena for `friendship.killer`

- ### `add`

Adds a single point to the named user.

- ### `dep`

Removes a single pont from the named user.

## `sheet`

The `sheet` command are used to interface with GoogleSheets directly from Discord. The general format it follows is `!sheet ACTION ACTION_SPECIFICS`. All sheets Alphonse has access to are in a specific parent folder inside Evan's GoogleDrive. The main actions are as follows:

- ### `build`
  This creates a new sheet with a user specified name. Optional: specifying `fencing` before the name tells Alphonse to build a sheet formatted for VTFC data collection purposes (having tabs for inventory and for fencing, and prefilled squares). Several commands can only be used with this fencing format.
  - `SHEET_NAME` The name you would like to give your newly created sheet. 

- ### `get`
  This gets specified data and returns it to the user.
  - `list` This has Alphonse send a list of the current sheets inside the parent folder to the channel from which the command was called.
  - `plot` This has Alphonse send a plot of the specified data. Only works for sheets build with fencing, or formatted respectively.
    - `bar/pie/line` Choosing one of these options generates a barchar, piechart, and line plot respectively. Line plots cannot be called for `inventory`.
      - `attendance/inventory` Data type for the plot.
        - `SHEET_NAME` Location of the data.
  
  - `SHEET_NAME` Returns an embeded link to the specified sheet.
 
    
- ### `set`
  Allows the caller to change data.
  - `curr` Sets a shortcut for a sheet commonly in use.
    - `SHEET_NAME` The sheet name you would like to assign to `curr`
      
  - `attendance` Sets attendance for the date the command was called on
    - `# WEAPON_NAME`x3 Inputted values for the numbers attending practice.
      - `SHEET_NAME` The sheet you want the attendance data to be saved to.
        
  - `inventory` Sets inventory data
    - `# ITEM_NAME`x1 The item you want to mark as broken or fixed.
      - `broken/fixed` If broken is specified, the specified number is added to the value in the sheet. If fixed, that number is removed from the value in the sheet.
        - `SHEET_NAME` The sheet you want the data to be saved to. 
          
- ### `delete`
  Deletes the specified sheet.
  - `SHEET_NAME`
    - `confirm` Without adding this to the end, the sheet won't be deleted.
   
- ### `flowchart`

  Called without `!sheet` before it; links to the `sheet` section of the README.
      
- ### SHORTCUTS:
  For ease, commands commonly called have been given shortcuts. Shortcuts do not need !sheet in front of them. If a shortcutted command takes normally `SHEET_NAME` at the end, leaving it off here will just apply the command to the in-use sheet (set by `!sheet set curr SHEET_NAME`)
  - `!plot` Takes the same values as the long version of `!sheet get plot`
  - `!inv` Takes the same values as the long version of `!sheet set inventory`
  - `!att` Takes the same values as the long version of `!sheet set attendance`

- ### EXAMPLE COMMANDS:

  - `!sheet build fencing Fall 2023`

  - `!sheet set curr Fall 2023`

  - `!att 10 epee 9 foil 12 sabre` (alternatively: `!att 10 e 9 f 12 s`)

  - `!inv 3 foil body cord broken` (alternatively: `!inv 3 rowbc broken`, where `rowbc` is short for right-of-way bodycord)

  - `!sheet get list`

  - `!sheet delete test confirm`

  - `!plot pie attendance` (alternatively: `!plot pie a`)

  - `!sheet delete Fall 2023 confirm`

Further shortcuts for named variables exist, following the pattern given directly above; i.e. `epee` is the same as `e`, `epee bodycord` is the same as `ebc`, and `maskcord` is the same as `mc`.

## `Wisdom`

This deals with retrieving and submitting quotes from users.

- ### `wisdom`

Alphonse prints out a randomly selected quote from the collection he has access to.

- ### `quote.submit`

Alphonse saves a quote, and the user supplying the quote, to a text file which `wisdom` pulls from. Quotes can be submitted either by typing something in the same message that the command is called in, or by calling the command while replying to a message.

## `tournament`

When this command is called, Alphonse will create a new role named 'tournament' and add anyone who reacts to the message to the role. This role can be mentioned via '@', and will allow for only users going to the tournament to be pinged, instead of having to use '@everyone' loosely.

## `new.members`

Gets the roles of any member who joined past the start date of whatever semester the command is called during (Fall or Spring). If the command is called in the middle of December or in the summer, the bot assumes the most recent semester is to be accessed.

## `source`

Returns an embedded link to Alphonse's GitHub homepage (here!).

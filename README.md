# A man walks down the street<br>it's a street in a strange world

## TODO:
- move sensitive info out of the main.py
- make it so that quote.submit will record responses. if it does record a response, credit the quote to the original message
- Make Al post rules that go along with most.dangerous.game when it is called. Make sub-commands (or external link) so that people can see their own scores.
- Make a command accessible only by me that will kill every active process.
- Make sheet.build with no name not get too specific with the time


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

### `sheet.build`

Creates a Google sheet and puts it in specific parent folder. If text is given, that is the sheet title. If no text is given, the time of the creation is used as the title.

### `sheet.delete`

Deletes a specific Google sheet. The text the user puts in is taken as the title of the sheet the user wants deleted. Type the word 'confirm' at the end of the title to confirm your command.

### `sheet.get`

Embeds a url link to the current in-use sheet.

### `sheet.list`

Returns a list of every sheet in the parent folder.

### `source`

Reterns an embedded link to Alphonse's GitHub homepage (here!).



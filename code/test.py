import os
from dotenv import load_dotenv
import json

load_dotenv()

a = os.getenv('DISCORD_TOKEN')
b = os.getenv('GUILD_TOKEN')
c = json.loads(os.environ['SHEETS_ID'])


print(a)
print(b)
print(c[1])

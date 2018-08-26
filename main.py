import discord
from discord.ext import commands

from GameManagement.game_manager import GM
from LangManagement.lang_manager import Lang
from LangManagement.prefix_manager import Prefix
from Util.dtable import DTable

#region INIT
Lang.init()
Prefix.init()
GM.init()
DTable.init()
#endregion

async def get_pre(client, message):
	return Prefix.get(message.guild.id)

bot = commands.Bot(command_prefix=get_pre, description='play a game')

#region EVENT
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name='.help to start playing'))
	print("Ready")

@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	await bot.process_commands(message)
#endregion

#region COGS
initial_extensions = ['game', 'admin', 'lang']

# Here we load our extensions(cogs) listed above in [initial_extensions].
if __name__ == '__main__':
	for extension in initial_extensions:
		try:
			bot.load_extension(extension)
		except Exception as e:
			print(f'Failed to load extension {extension}.')
#endregion

with open("token.txt", "r") as file:
	token = file.read().strip()
bot.run(token)

import discord
from discord.ext import commands

from GameManagement.game_manager import GM, GameCreationError
from GameManagement.lobby_manager import LM, LobbyError
from GameManagement.game_wrapper import GW
from LangManagement.lang_manager import Lang
from LangManagement.prefix_manager import Prefix
from Util.dlist import DList
from Util.dtable import DTable


async def get_pre(client, message):
	return Prefix.get(message.guild.id)

bot = commands.Bot(command_prefix=get_pre, description='play a game')
Lang.init()
Prefix.init()
GM.init()
DTable.init()

# region EVENTS
@bot.event
async def on_ready():
	await bot.change_presence(activity=discord.Game(name='.help to start playing'))
	print("Ready")


@bot.event
async def on_message(message):
	if message.author == bot.user:
		return
	await bot.process_commands(message)


@bot.command(pass_context=True)
async def test(ctx):
	await ctx.send("test \n sauce")
# endregion


# region LANGUAGE AND PREFIX MANAGEMENT
@bot.command(pass_context=True, brief="Set the command prefix for this server")
async def prefix(ctx, *args):
	if len(args) == 0:
		await ctx.send(Lang.get_text("prefix", ctx))
	else:
		Prefix.set(ctx.message.guild.id, " ".join(args))
		await ctx.send(Lang.get_text("prefix_success", ctx))


@bot.command(pass_context=True, brief="Set the main language of the channel")
async def mainlang(ctx, *args):
	if len(args) == 0:
		await ctx.send(Lang.get_text("mainlang", ctx))
	else:
		language = "_".join(args)
		try:
			Lang.set_main_lang(ctx.message.channel.id, language)
			await ctx.send(Lang.get_text("mainlang_success", ctx).format(Lang.get_main_lang(ctx.message.channel.id)))
		except KeyError:
			await ctx.send(Lang.get_text("not_a_language", ctx).format(language))


@bot.command(pass_context=True, aliases=["addlanguage"], brief="Add a language to the channel")
async def addlang(ctx, *args):
	if len(args) == 0:
		await ctx.send(Lang.get_text("addlang", ctx))
	else:
		language = "_".join(args)
		try:
			Lang.add_lang(ctx.message.channel.id, language)
			await ctx.send(Lang.get_text("addlang_success", ctx).format(Lang.get_language(language)))
		except KeyError:
			await ctx.send(Lang.get_text("not_a_language", ctx).format(language))


@bot.command(pass_context=True, alisases=["removelang", "rmlanguage", "removelanguage"], brief="Remove a language from the channel")
async def rmlang(ctx, *args):
	if len(args) == 0:
		await ctx.send(Lang.get_text("rmlang", ctx))
	else:
		language = "_".join(args)
		try:
			Lang.rm_lang(ctx.message.channel.id, language)
			await ctx.send(Lang.get_text("rmlang_success", ctx).format(Lang.get_language(language)))
		except KeyError:
			await ctx.send(Lang.get_text("not_a_language", ctx).format(language))


@bot.command(aliases=["language"], brief="List the channel's languages")
async def lang(ctx):
	langlist = Lang.get_secondary_lang(ctx.message.channel.id)
	if len(langlist) == 0:
		msglist = Lang.get_text("none", ctx)
	else:
		msglist = DList.get(langlist)
	await ctx.send(Lang.get_text("lang", ctx).format(Lang.get_main_lang(ctx.message.channel.id), msglist))
# endregion


# region GAMES COMMAND
@bot.command(aliases=["gamelist"], brief="List every playable games in this lobby")
async def games(ctx):
	chan = ctx.message.channel.id
	msg = DTable.get_table(DTable.gamelistlabels[Lang.best_lang(Lang.gotoh_id, chan)], GM.get_list(Lang.get_langs(chan)))
	await ctx.send(msg)


@bot.command(aliases=["lobbies"], brief="List every parties waiting for players")
async def lobby(ctx, *args):
	chan = ctx.message.channel
	lobbies = LM.lobby(chan.guild.id, Lang.get_langs(chan.id), args)
	msg = DTable.get_table(DTable.lobbylistlabels[Lang.best_lang(Lang.gotoh_id, chan.id)], lobbies)
	await ctx.send(msg)


@bot.command(pass_context=True, brief="Create a party")
async def play(ctx, *args):
	if len(args) == 0:
		await ctx.send(Lang.get_text("play", ctx))
	else:
		try:
			try:
				handler = GM.get_handler(args, ctx)
				LM.add_handler(handler, ctx.message.author.id, ctx.message.channel.guild.id, ctx)
				if handler.player_count.isdigit():
					# There is a fixed amount of players, the game will start automatically
					await ctx.send(	Lang.get_text("play_success_regular", ctx)
									.format(ctx.message.author.display_name, handler.get_name(Lang.get_langs(ctx.message.channel.id))))
				else:
					# There isn't a fixed amount of players, !start will be required
					await ctx.send(	Lang.get_text("play_success_flex", ctx)
									.format(ctx.message.author.display_name, handler.get_name(Lang.get_langs(ctx.message.channel.id))))
			except LobbyError as err:
				await ctx.send(err.message.format(ctx.message.author.display_name))
		except GameCreationError as err:
			await ctx.send(err.message)


@bot.command(pass_context=True, brief="Disband your party")
async def cancel(ctx):
	try:
		LM.rm_handler(ctx.message.author.id, ctx.message.channel.guild.id, ctx)
		await ctx.send(Lang.get_text("cancel_success", ctx).format(ctx.message.author.display_name))
	except LobbyError as err:
		await ctx.send(err.message.format(ctx.message.author.display_name))

@bot.command(pass_context=True, brief="Join a game by the host name")
async def join(ctx, *args):
	try:

# endregion

with open("token.txt", "r") as file:
	token = file.read().strip()
bot.run(token)

from discord.ext import commands
from Util.dtable import DTable
from LangManagement.lang_manager import Lang
from GameManagement.game_manager import GM, GameCreationError
from GameManagement.lobby_manager import LM, LobbyError


class GameCog:
	def __init__(self, bot):
		self.bot = bot
		# {channel_id : game handler}
		self.ghs = {}

	@commands.command(aliases=["gamelist"], brief="List every playable games in this lobby")
	async def games(self, ctx):
		chan = ctx.message.channel.id
		msg = DTable.get_table(DTable.gamelistlabels[Lang.best_lang(Lang.gotoh_id, chan)], GM.get_list(Lang.get_langs(chan)))
		await ctx.send(msg)

	@commands.command(aliases=["lobbies"], brief="List every parties waiting for players")
	async def lobby(self, ctx, *args):
		chan = ctx.message.channel
		lobbies = LM.lobby(ctx.message.author.id, chan.guild.id, Lang.get_langs(chan.id), args)
		msg = DTable.get_table(DTable.lobbylistlabels[Lang.best_lang(Lang.gotoh_id, chan.id)], lobbies)
		await ctx.send(msg)

	@commands.command(pass_context=True, brief="Create a party")
	async def play(self, ctx, *args):
		# Check if the bot can manage roles and create channels
		permissions = ctx.message.channel.guild.me.guild_permissions
		if permissions.manage_channels:
			if permissions.manage_roles:
				# Check if the users provided at least 1 argument
				if len(args) == 0:
					await ctx.send(Lang.get_text("play", ctx))
				else:
					try:
						try:
							# Get a game handler objects
							handler = GM.get_handler(args, ctx)
							# Add the handler to the lobby
							LM.add_handler(handler, ctx.message.author.id, ctx.message.channel.guild.id, ctx)
							# Check if there's a fixed amount of players
							if handler.player_cap.min == handler.player_cap.max:
								# There is a fixed amount of players, the game will start automatically when enough players have joined
								await ctx.send(Lang.get_text("play_success_regular", ctx)
											   .format(ctx.message.author.display_name, handler.get_name(Lang.get_langs(ctx.message.channel.id))))
							else:
								# There isn't a fixed amount of players, !start will be required
								await ctx.send(Lang.get_text("play_success_flex", ctx)
											   .format(ctx.message.author.display_name, handler.get_name(Lang.get_langs(ctx.message.channel.id))))
						except LobbyError as err:
							await ctx.send(err.message.format(ctx.message.author.display_name))
					except GameCreationError as err:
						await ctx.send(err.message)
			else:
				print("")
		else:
			print("")

	@commands.command(pass_context=True, brief="Disband your party")
	async def cancel(self, ctx):
		try:
			LM.rm_handler(ctx.message.author.id, ctx.message.channel.guild.id, ctx)
			await ctx.send(Lang.get_text("cancel_success", ctx).format(ctx.message.author.display_name))
		except LobbyError as err:
			await ctx.send(err.message.format(ctx.message.author.display_name))

	@commands.command(pass_context=True, brief="Join a game by the host name")
	async def join(self, ctx, *args):
		if len(args) == 0:
			await ctx.send(Lang.get_text("join", ctx))
		else:
			user_id = ' '.join(args)
			try:
				# Add the player to the right handler (if found)
				handler = LM.add_player_to_lobby(ctx.message.author, user_id, ctx.message.channel.guild.id, ctx)

				await ctx.send(Lang.get_text("join_succes", ctx).format(ctx.message.author.display_name, handler.players[0].name))
				# Check if the handler is at full capacity
				if handler.player_cap.is_max(len(handler.players)):
					await ctx.send("THIS IS WERE I SHOULD START THE GAME")
					gamehandler = handler.start()
					# Remove the handlers from the waiting handlers
					LM.remove_waiting(handler, ctx.message.author.id, ctx.message.channel.guild.id)
					# Give the bot instance to the game handler
					gamehandler.bot = self.bot
					# Create the channels
					channels = await gamehandler.channels()
					# Register the handler in the channels
					for channel in channels:
						self.ghs[channel] = gamehandler
					# Start the game
					await gamehandler.start()

			except LobbyError as err:
				await ctx.send(err.message)


	# TODO: COMMAND OPEN TO LET OTHER SERVERS JOIN YOUR PARTY (need to be host of a waiting party)


def setup(bot):
	bot.add_cog(GameCog(bot))

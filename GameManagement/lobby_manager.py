from LangManagement.lang_manager import Lang
from GameManagement.player import Player


class LobbyError(Exception):
	def __init__(self, message):
		self.message = message


class LM:
	# {server_id: [handler1, handler2 ...]}
	waiting_handler_serv = {}
	# {(user_id, server_id): handler}
	waiting_handler_usr = {}

	#region PRIVATE METHOD
	@staticmethod
	def is_game_to_be_listed(handler, gamenames, player_id):
		# Return True if the player is the host of said handler
		if handler.players[0].id == player_id:
			return True
		# Checks if the player wants every game
		if len(gamenames) == 0:
			# Check if the player is invited in the game
			if len(handler.guests) == 0:
				return True
			else:
				for guest in handler.guests:
					if guest.id == player_id:
						return True
				return False
		else:
			for gamename in gamenames:
				gamename = gamename.lower().replace("_", " ")
				for name in handler.names:
					if name.lower() == gamename:
						# Check if the player is invited in the game
						if len(handler.guests) == 0:
							return True
						else:
							for guest in handler.guests:
								if guest.id == player_id:
									return True
							return False
			return False

	@staticmethod
	def scan_serv_for_lobbies(lobbylist, handlers, langs, player_id, gamenames):
		for handler in handlers:
			# Checks if the game is in the list the user asked
			if LM.is_game_to_be_listed(handler, gamenames, player_id):
				# Scans the languages of the game
				for lang in langs:
					if lang in handler.names:
						# A commmon lang has been found with the channel
						argstr = ""
						for argname, argval in handler.args.items():
							if argval is None:
								argstr += f"{argname}"
							else:
								argstr += f"{argname}={argval} "
						party = {
							"name": handler.names[lang],
							"players": f"{len(handler.players)}/{str(handler.player_cap)}",
							"args": argstr,
							"host": handler.players[0].get_name(),
						}
						lobbylist.append(party)
						break

	@staticmethod
	def lobby_search(hostid, server_id):
		# No tag found, but the user could have write !join playername(#disc) or !join nickname
		# Checks if the user typed !join playername#disc
		user_id = hostid.strip().lower()
		matches = []
		if Player.is_discord_name(user_id):
			for handler in LM.waiting_handler_serv[server_id]:
				if handler.matches_host_exact(user_id):
					matches.append(handler)
					break
			# if nothing was found, we look on the online game
			if len(matches) == 0:
				for handler in LM.waiting_handler_serv[0]:
					if handler.matches_host_exact(user_id):
						matches.append(handler)
						break
		else:
			# Search broadly (name, nickname etc) locally
			for handler in LM.waiting_handler_serv[server_id]:
				if handler.matches_host(user_id):
					matches.append(handler)
			# Search broadly online
			for handler in LM.waiting_handler_serv[0]:
				if handler.matches_host(user_id):
					matches.append(handler)
		return matches
	#endregion

	@staticmethod
	def lobby(player_id, server_id, langs, gamenames):
		parties = []
		# Scans the local games
		if server_id in LM.waiting_handler_serv:
			LM.scan_serv_for_lobbies(parties, LM.waiting_handler_serv[server_id], langs, player_id, gamenames)

		# Scans the online games
		LM.scan_serv_for_lobbies(parties, LM.waiting_handler_serv[0], langs, player_id, gamenames)
		return parties

	# RESTRICTION: A user cannot host more than 1 lobby on any server
	@staticmethod
	def add_handler(handler, user_id, server_id, ctx):
		# Checks if the user is already hosting a lobby
		if (user_id, server_id) in LM.waiting_handler_usr or (user_id, 0) in LM.waiting_handler_usr:
			raise LobbyError(Lang.get_text("already_host", ctx))
		# Add the handler to waiting_handler_serv
		if handler.online:
			# Add the handler to waiting_handler_usr
			LM.waiting_handler_usr[(user_id, 0)] = handler
			# Add the handler to waiting_handler_serv
			LM.waiting_handler_serv[0].append(handler)
		else:
			# Add the handler to waiting_handler_usr
			LM.waiting_handler_usr[(user_id, server_id)] = handler
			# Add the handler to waiting_handler_serv
			if server_id in LM.waiting_handler_serv:
				LM.waiting_handler_serv[server_id].append(handler)
			else:
				LM.waiting_handler_serv[server_id] = [handler]

	@staticmethod
	def rm_handler(user_id, server_id, ctx):
		# Checks if there is a handler to remove
		if (user_id, server_id) not in LM.waiting_handler_usr:
			server_id = 0
			if (user_id, 0) not in LM.waiting_handler_usr:
				raise LobbyError(Lang.get_text("not_a_host", ctx))
		# Remove the handler from waiting_handler_usr
		del LM.waiting_handler_usr[(user_id, server_id)]

		# Search and remove the handler waiting_handler_serv
		for i, handler in enumerate(LM.waiting_handler_serv[server_id]):
			if handler.players[0].id == user_id:
				del LM.waiting_handler_serv[server_id][i]
				break

	@staticmethod
	def add_player_to_lobby(player, user_id, server_id, ctx):
		# Get the host tag
		tagged = ctx.message.mentions
		if len(tagged) > 0:
			# Get the handler associated
			host = tagged[0]
			matches = []
			if (host.id, server_id) in LM.waiting_handler_usr:
				matches.append(LM.waiting_handler_usr[(host.id, server_id)])
			elif (host.id, 0) in LM.waiting_handler_usr:
				matches.append(LM.waiting_handler_usr[(host.id, 0)])
			else:
				# No handler hosted by host was found
				raise LobbyError(Lang.get_text("no_host", ctx).format(f"{host.name}#{host.discriminator}"))
		else:
			# Host wasn't tagged, another identifier was provided
			matches = LM.lobby_search(user_id, server_id)

		# Filter out the private lobby where player is not invited
		validmatches = []
		for handler in matches:
			print(handler.guests)
			if len(handler.guests) > 0:
				for guest in handler.guests:
					if player.id == guest.id:
						validmatches.append(handler)
						break
			else:
				validmatches.append(handler)

		if len(matches) == 0:
			# No handler hosted by user_id was found
			raise LobbyError(Lang.get_text("no_host", ctx).format(user_id))
		elif len(validmatches) == 0:
			# A handler hosted by user_id was found but player is not invited
			raise LobbyError(Lang.get_text("no_valid_host", ctx).format(user_id, player.display_name))
		elif len(validmatches) > 1:
			# Multiple valid handler were found
			raise LobbyError(Lang.get_text("multiple_host", ctx).format(user_id))

		# At this point there is 1 valid handler, in validmatches[0]
		validmatches[0].add_player(player)
		return validmatches[0]

	@staticmethod
	def remove_waiting(handler, host_id, server_id):
		# Remove the handler from waiting handler usr
		if (host_id, server_id) in LM.waiting_handler_usr:
			del LM.waiting_handler_usr[(host_id, server_id)]
		elif (host_id, 0) in LM.waiting_handler_usr:
			del LM.waiting_handler_usr[(host_id, 0)]
		# Remove the handler from waiting handler serv
		LM.waiting_handler_serv[server_id].remove(handler)


# LISTE DES JEUX INTER SERVEUR
# POSTULAT: AUCUN SERVEUR DISCORD N'A L'ID 0
LM.waiting_handler_serv[0] = []

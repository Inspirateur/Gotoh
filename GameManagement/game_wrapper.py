from GameManagement.player import Player


class GW:
	def __init__(self, args, player_cap, gameclass, names, gamefolder, guests=None, online=False):
		self.args = args
		self.players = []
		self.player_cap = player_cap
		self.gameclass = gameclass
		self.guests = guests
		self.names = names
		self.gamefolder = gamefolder
		self.online = online

	def start(self):
		return self.gameclass(self.args, self.players, self.names, self.gamefolder, self.online)

	def get_name(self, chanlangs):
		# Get the name in the best lang for the channel
		for lang in chanlangs:
			if lang in self.names:
				return self.names[lang]
		# If nothing was found return a name at random
		for name in self.names.values():
			return name

	def add_player(self, ctx):
		self.players.append(Player(ctx))


	# ASSERT: discordname is in lower case
	def matches_host_exact(self, discordname):
		return discordname == f"{self.players[0].name.lower()}#{self.players[0].discriminator.lower()}"

	# ASSERT: indent is in lower case
	def matches_host(self, ident):
		return ident == self.players[0].name.lower() or ident == f"{self.players[0].name.lower()}#{self.players[0].discriminator.lower()}" \
			   or ident == self.players[0].id or ident == self.players[0].nick.lower()
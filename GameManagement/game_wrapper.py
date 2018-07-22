from GameManagement.player import Player


class GW:
	def __init__(self, args, player_count, gameclass, names, guests=None, online=False):
		self.args = args
		self.players = []
		self.player_count = player_count
		self.gameclass = gameclass
		self.guests = guests
		self.names = names
		self.online = online

	def start(self):
		pass

	def get_name(self, chanlangs):
		# Get the name in the best lang for the channel
		for lang in chanlangs:
			if lang in self.names:
				return self.names[lang]
		# If nothing was found return a name at random
		for name in self.names.values():
			return name

	def add_player(self, discord_member):
		self.players.append(Player(discord_member.id, discord_member.name, discord_member.discriminator, discord_member.display_name, discord_member.avatar_url))

	# ASSERT: discordname is in lower case
	def matches_host_exact(self, discordname):
		return discordname == f"{self.players[0].name.lower()}#{self.players[0].discriminator.lower()}"

	# ASSERT: indent is in lower case
	def matches_host(self, ident):
		return ident == self.players[0].name.lower() or ident == f"{self.players[0].name.lower()}#{self.players[0].discriminator.lower()}" \
			   or ident == self.players[0].id or ident == self.players[0].nick.lower()
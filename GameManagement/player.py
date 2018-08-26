from LangManagement.lang_manager import Lang

class Player:
	# returns true for in name matches *#decimal with 4 <= len(decimal) <= 6, false otherwise
	# ASSERT: DISCORD DISCRIMINATOR IS BETWEEN 4 AND 6 DIGIT LONG
	@staticmethod
	def is_discord_name(name):
		length = len(name)
		i = length - 1
		while i > 0 and name[i].isdecimal():
			i -= 1
		return i > 0 and name[i] == '#' and 4 < length - i < 7

	def __init__(self, ctx):
		self.user = ctx.message.author
		self.id = ctx.message.author.user_id
		self.name = ctx.message.author.name
		self.nick = ctx.message.author.display_name
		self.discriminator = ctx.message.author.discriminator
		self.avatar = ctx.message.author.avatar
		self.server = ctx.message.channel.guild
		self.langs = Lang.get_langs(ctx.message.channel.id)
		self.category_id = ctx.message.channel.category_id
		self.channel = None
		self.role = None
		self.bestlang = None

	def assign_channel(self, channel):
		self.channel = channel

	def get_name(self):
		return f"{self.name}#{self.discriminator}"

import re


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

	def __init__(self, user_id, name, discriminator, display_name, avatar):
		self.id = user_id
		self.name = name
		self.nick = display_name
		self.discriminator = discriminator
		self.avatar = avatar
		self.channel = None

	def assign_channel(self, channel):
		self.channel = channel

	def get_name(self):
		return f"{self.name}#{self.discriminator}"

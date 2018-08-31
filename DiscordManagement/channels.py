from .roles import *
from discord.permissions import PermissionOverwrite


async def player_channel(gamename, guild, player, category=None):
	# TODO: Check if the channel name is already taken to make sure it's unique
	# Create the channel and assign it to the player
	channel = await guild.create_text_channel(name=f"{player.nick}-{gamename}", category=category)
	player.channel = channel
	# Create the player role
	role = await player_role(gamename, guild, player)
	# spectator can't write in the player channel
	overwrite = PermissionOverwrite()
	overwrite.send_messages = False
	await channel.set_permissions(target=guild.default_role, overwrite=overwrite)
	# player can write in its player channel
	overwrite = PermissionOverwrite()
	overwrite.send_messages = True
	await channel.set_permissions(target=role, overwrite=overwrite)
	# gotoh can write in the player channel
	await channel.set_permissions(target=guild.me, overwrite=overwrite)


async def game_channel(gamename, guild, players, category=None):
	# TODO: Check if the channel name is already taken to make sure it's unique
	# Create the channel and assign it to every player
	channel = await guild.create_text_channel(name=f"{gamename}", category=category)
	for player in players:
		player.channel = channel
	# spectator can't write in the game channel
	role = await game_role(gamename, guild, players)
	overwrite = PermissionOverwrite()
	overwrite.send_messages = False
	await channel.set_permissions(target=guild.default_role, overwrite=overwrite)
	# player can write in the game channel
	overwrite = PermissionOverwrite()
	overwrite.send_messages = True
	await channel.set_permissions(target=role, overwrite=overwrite)
	# gotoh can write in the game channel
	await channel.set_permissions(target=guild.me, overwrite=overwrite)


async def exclude_player_from_chan(channel, playerrole):
	overwrite = PermissionOverwrite()
	overwrite.read_messages = False
	await channel.set_permissions(target=playerrole, overwrite=overwrite)
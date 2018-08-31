async def player_role(gamename, guild, player):
	# TODO: Check if the role name is already taken to make sure it's unique
	role = await guild.create_role(name=f"{player.nick}-{gamename}")
	player.role = role
	await player.user.add_roles(role)
	return role


async def game_role(gamename, guild, players):
	# TODO: Check if the role name is already taken to make sure it's unique
	role = await guild.create_role(name=f"{gamename}")
	for player in players:
		player.role = role
		await player.user.add_roles(role)
	return role
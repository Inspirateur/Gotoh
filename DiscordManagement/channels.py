async def player_channel(name, guild, player, rolename, category=None):
	channel = await guild.create_text_channel(name, category)
	player.channel = channel
	role = await guild.create_role(name=rolename)
	player.role = role
	await player.user.add_roles(role)
	await channel.set_permission(guild.default_role, send_message=False)
	await channel.set_permission(role, send_message=True)
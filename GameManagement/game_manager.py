import copy
import importlib
import os
from collections import OrderedDict

import yaml

from GameManagement.game_wrapper import GW
from GameManagement.player import Player
from LangManagement.lang_manager import Lang
from Util.dlist import DList
from GameManagement.player_cap import PC


class GameCreationError(Exception):
	def __init__(self, message):
		self.message = message


class GM:
	# region ARG CHEKING METHODS
	@staticmethod
	def is_any(x):
		return True

	@staticmethod
	def is_int(x):
		try:
			int(x)
			return True
		except ValueError:
			return False

	@staticmethod
	def is_percentage(x):
		try:
			f = float(x)
			return 0 <= f <= 100
		except ValueError:
			return False

	arg_type = {
		"int": is_int,
		"int+": str.isdecimal,
		"word": str.isalpha,
		"%": is_percentage
	}
	# endregion

	# region GAMES DATA
	# {Dossier1 : {handler:file.class, name:{en:Game1, fr:Jeu1}, args:arguments, ...}, ...}
	# Used to make the game list
	gamefiles = {}
	# {Game1: {handler:file.class, name:{en:Game1, fr:Jeu1}, args:{arg1:(fct1, str1), arg2:(fct2, str2)}, ...}, ...}
	# Used to return the handler given the name of the game in any language
	gamenames = {}
	games_path = "Games"
	# endregion

	# region PRIVATE METHODS
	@staticmethod
	def load_args(game):
		# Change the arguments from text to dicts
		arglist = game["args"].split(" ")
		argdict = OrderedDict()
		# For every argument
		for arg in arglist:
			if len(arg) > 0:
				# If it's a <value>
				if arg.startswith("<"):
					eqindex = arg.find("=", 1)
					if eqindex != -1:
						# it's <name=type>
						name = arg[1:eqindex]
						cat = arg[eqindex + 1:-1]
					else:
						# it's <type>
						name = arg[1:-1]
						cat = name
					if cat in GM.arg_type:
						# type is a native arg type
						cat = (GM.arg_type[cat], cat)
					else:
						if cat.startswith("[") and cat.endswith("]"):
							# it's <name=[valuelist]>
							values = cat[1:-1].split(",")
							valuelist = []
							for value in values:
								valuelist.append(value.strip())
							cat = (lambda x: x in valuelist, cat)
						else:
							# it's <name=type> but type is not native
							cat = (GM.is_any, arg[eqindex + 1:-1])
				# If it's raw_text
				else:
					name = arg
					cat = (True, arg)
				argdict[name] = cat
		game["args"] = argdict

	@staticmethod
	def init():
		gamedir = os.listdir(GM.games_path)
		# Runs through every game folder
		for file in gamedir:
			filename = str(file)
			try:
				# Open the game folder <filename> meta file
				with open(f"{GM.games_path}\{filename}\meta.txt") as mfile:
					# Load the meta file into gamefiles[filename]
					GM.gamefiles[filename] = yaml.load(mfile)
					# Change "players" entry to a Player Cap class
					GM.gamefiles[filename]["players"] = PC(str(GM.gamefiles[filename]["players"]))
					# DeepCopy this entry into gamenames for every name/lang the game has
					for gamename in GM.gamefiles[filename]["name"].values():
						gamename = gamename.lower()
						GM.gamenames[gamename] = copy.deepcopy(GM.gamefiles[filename])
						GM.gamenames[gamename]["folder"] = filename
						# If the Game has arguments
						if "args" in GM.gamenames[gamename]:
							# Parse the args from pure string to dict with check functions
							GM.load_args(GM.gamenames[gamename])
			except (OSError, yaml.YAMLError):
				print(f"Could not load {filename}\meta.txt")

	@staticmethod
	def get_best_lang(langs, game):
		for lang in langs:
			if lang in game["name"]:
				return lang
		return None

	@staticmethod
	def parse_args(args_it, gamename, ctx):
		args = {}
		game_args = GM.gamenames[gamename]["args"]
		game_args_it = iter(game_args.items())
		for arg in args_it:
			# Check if the user arg is name=value or value
			eq_index = arg.find("=")
			if eq_index == -1:
				# arg is value, the 1st fitting argument from order in game args will be chosen
				for game_arg in game_args_it:
					if game_arg[1][0] is True:
						# A fitting argument was found
						args[game_arg[0]] = None
						break
					elif game_arg[1][0](arg):
						# A fitting argument was found
						args[game_arg[0]] = arg
						break
				else:
					# No matching arguments were found
					raise GameCreationError(Lang.get_text("no_arg_found", ctx).format(arg, gamename))
			else:
				# arg is name=value, game_args[name](value) must be True
				name = arg[:eq_index]
				value = arg[eq_index+1:]
				if name in game_args:
					# The name exists
					if game_args[name][0] is True:
						# The value is correct
						args[name] = None
					elif game_args[name][0](value):
						args[name] = value
					else:
						# The value is wrong
						raise GameCreationError(Lang.get_text("bad_arg_value", ctx).format(value, game_args[name][1]))
				else:
					# The args doesn't exist
					raise GameCreationError(Lang.get_text("not_a_arg", ctx).format(name, value, gamename))
		return args

	@staticmethod
	def get_id_from_tag(tag):
		return int(''.join(filter(lambda x: x.isdigit(), tag)))
	# endregion

	# region PUBLIC METHODS
	@staticmethod
	def get_list(langs):
		gamelist = []
		for game in GM.gamefiles.values():
			lang = GM.get_best_lang(langs, game)
			if lang:
				try:
					args = str(game["args"])
				except KeyError:
					args = ""
				try:
					devs = DList.get(game["devs"], effect="")
				except KeyError:
					devs = ""
				try:
					gamelist.append({
						"name": str(game["name"][lang]), "players": str(game["players"]),
						"args": args, "devs": devs})
				except KeyError:
					pass
		return gamelist

	# Suppose that there's no overlapping on name translation between different games (ie Jeu1 != Game2)
	@staticmethod
	def get_handler(command, ctx):
		# Remove player tags from the end of the command
		tags = []
		for arg in reversed(command):
			if arg.startswith("<@") and arg.endswith(">"):
				tags.append(GM.get_id_from_tag(arg))
			else:
				break
		if len(tags) > 0:
			command = command[:-len(tags)]
		# Get the guests from the command message
		guests = []
		for member in ctx.message.mentions:
			# Check if it is a guest tag or an arg tag
			if member.id in tags:
				guests.append(Player(member.id, member.name, member.discriminator, member.display_name, member.avatar_url))
		print("guests", guests)
		# Extract tags if there is any
		args_it = iter(command)
		# Check if the game exists
		try:
			gamename = next(args_it).lower().replace("_", " ")
			if gamename not in GM.gamenames:
				raise GameCreationError(Lang.get_text("not_a_game", ctx).format(command[0]))
		except StopIteration:
			raise GameCreationError(Lang.get_text("play", ctx))
		# Check if there is an appropriate language for the game and channel
		langs = Lang.get_langs(ctx.message.channel.id)
		game = GM.gamenames[gamename]
		bestlang = GM.get_best_lang(langs, game)
		if bestlang is None:
			raise GameCreationError(Lang.get_text("no_common_lang", ctx).format(gamename))
		# Parse the args
		args = GM.parse_args(args_it, gamename, ctx)
		# At this point args contains the user args and they're all correct (or an error was raised and caught in main)
		handlerdata = game['handler'].split(".")
		hfile = handlerdata[0]
		hclassname = handlerdata[1]
		hmodule = importlib.import_module(f"Games.{game['folder']}.{hfile}")
		hclass = getattr(hmodule, hclassname)
		if "multilang" not in game or game["multilang"]:
			names = game["name"]
		else:
			names = {bestlang: game["name"][bestlang]}
		wrapper = GW(args, game["players"], hclass, names, guests)
		wrapper.add_player(ctx.message.author)
		return wrapper
	# endregion

import os

import yaml

from LangManagement.prefix_manager import Prefix
from Util.dlist import DList


class Lang:
	lang2iso = {}
	iso2lang = {}
	chans = {}
	texts = {}
	gotoh_id = "Gotoh"
	home = os.getcwd()
	cwd = os.getcwd() + "\LangManagement"
	@staticmethod
	def init():
		# Initialize chans dict as {chan: [lang1, lang2...]}
		with open(f"{Lang.cwd}\chans.txt", "r") as file:
			Lang.chans = yaml.load(file)
		# Initialize langs dict as {english language name: ISO code}
		with open(f"{Lang.cwd}\lang.txt", "r") as file:
			for line in file:
				data = line.split("\t")
				language = data[1][:-1]
				iso = data[0]
				Lang.iso2lang[iso] = language
				Lang.lang2iso[language] = iso
		# Load gotoh's lang files
		Lang.load_text(Lang.gotoh_id, "fr")
		Lang.load_text(Lang.gotoh_id, "en")
		# Until github manager handles it, it's done manually
		Lang.load_text("Tic-Tac-Toe", "fr")
		Lang.load_text("Tic-Tac-Toe", "en")

# --- CHANNEL LANGUAGES MANAGEMENT ---
	@staticmethod
	def get_iso(lang):
		if lang in Lang.iso2lang:
			return lang
		else:
			return Lang.lang2iso[lang]

	@staticmethod
	def get_language(iso):
		if iso in Lang.lang2iso:
			return iso
		else:
			return Lang.iso2lang[iso]

	@staticmethod
	def register_channel(chan):
		Lang.chans[chan] = []
		Lang.add_lang(chan, "en")

	@staticmethod
	def rm_lang(chan, lang):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		try:
			Lang.chans[chan].remove(Lang.get_iso(lang))
		except ValueError:
			pass
		if len(Lang.chans[chan]) == 0:
			Lang.add_lang(chan, "en")
		with open(f"{Lang.cwd}\chans.txt", "w") as file:
			yaml.dump(Lang.chans, file, default_flow_style=False)

	@staticmethod
	def add_lang(chan, lang):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		iso = Lang.get_iso(lang)
		if iso not in Lang.chans[chan]:
			Lang.chans[chan].append(iso)
		with open(f"{Lang.cwd}\chans.txt", "w") as file:
			yaml.dump(Lang.chans, file, default_flow_style=False)

	@staticmethod
	def set_main_lang(chan, lang):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		iso = Lang.get_iso(lang)
		try:
			Lang.chans[chan].remove(iso)
			Lang.chans[chan].insert(0, iso)
		except ValueError:
			Lang.chans[chan][0] = iso
		with open(f"{Lang.cwd}\chans.txt", "w") as file:
			yaml.dump(Lang.chans, file, default_flow_style=False)

	@staticmethod
	def get_langs(chan):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		return Lang.chans[chan]

	@staticmethod
	def get_main_lang(chan):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		return Lang.iso2lang[Lang.chans[chan][0]]

	@staticmethod
	def get_secondary_lang(chan):
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		sec_langs = Lang.chans[chan][1:]
		for i in range(len(sec_langs)):
			sec_langs[i] = Lang.iso2lang[sec_langs[i]]
		return sec_langs

	# --- GAME LANGUAGES MANAGEMENT ---
	@staticmethod
	def read_text_file(game_id, lang, file):
		Lang.texts[game_id][lang] = {}
		lastkey = None
		for line in file:
			if lastkey is None:
				data = line.split(">")
				if len(data) == 2:
					content = data[1].rstrip()
					if content.endswith("<"):
						Lang.texts[game_id][lang][data[0].strip()] = content[:-1].replace('"', '\\"').replace("'", "\\'")
						lastkey = None
					else:
						Lang.texts[game_id][lang][data[0].strip()] = content.replace('"', '\\"').replace("'", "\\'")
						lastkey = data[0].strip()
			else:
				# This is the continuation of a text
				data = line.rstrip()
				if data.endswith("<"):
					Lang.texts[game_id][lang][lastkey] += "\n"+data[:-1].replace('"', '\\"').replace("'", "\\'")
					lastkey = None
				else:
					Lang.texts[game_id][lang][lastkey] += "\n"+data.replace('"', '\\"').replace("'", "\\'")

	@staticmethod
	def load_text(game_id, lang=None):
		# Create game lang data if non existent
		if game_id not in Lang.texts:
			Lang.texts[game_id] = {}
		# Build the path of the game directory
		if game_id == Lang.gotoh_id:
			path = Lang.cwd
		else:
			path = f"{Lang.home}\Games\{game_id}"

		if lang is None:
			# Load every lang file in the directory path
			files = []
			# List every file in the directory path
			for (dirpath, dirnames, filenames) in os.walk(path):
				files.extend(filenames)
				break
			# Load every lang file in Lang.texts
			for file in files:
				if file.endswith(".txt"):
					pre = file.split(".")[0]
					if pre in Lang.lang2iso:
						with open(f"{path}\{file}", "r", encoding="utf-8") as f:
							Lang.read_text_file(game_id, pre, f)
		else:
			# Load the lang file "lang".txt in the directory path
			try:
				with open(f"{path}\{lang}.txt", "r", encoding="utf-8") as file:
					Lang.read_text_file(game_id, lang, file)
			except OSError as err:
				print(err)

	@staticmethod
	def best_lang(game_id, chan):
		# Checks if the channel is registered
		if chan not in Lang.chans:
			Lang.register_channel(chan)
		# Look for the first game language allowed for the channel
		for chan_lang in Lang.chans[chan]:
			if chan_lang in Lang.texts[game_id]:
				return chan_lang
		return "en"

	@staticmethod
	def get(game_id, text_id, chan, serv=None):
		# Get the most appropriate language for the game and chan
		language = Lang.best_lang(game_id, chan)
		# If a language was found and the text_id exists for this language
		if language in Lang.texts[game_id] and text_id in Lang.texts[game_id][language]:
			return Lang.get_from_lang(game_id, text_id, language, serv)
		else:
			return f"No text for id **{text_id}** and language {DList.get(Lang.chans[chan])}"

	@staticmethod
	def get_text(text_id, ctx):
		return Lang.get(Lang.gotoh_id, text_id, ctx.message.channel.id, ctx.message.guild.id)

	@staticmethod
	def get_from_lang(game_id, text_id, language, serv=None):
		if serv:
			return Lang.texts[game_id][language][text_id].replace("%%", Prefix.get(serv))
		else:
			#print(Lang.texts[game_id])
			#print(Lang.texts[game_id][language])
			return Lang.texts[game_id][language][text_id]

import collections

from LangManagement.lang_manager import Lang


class DTable:
	gamelistlabels = {}
	lobbylistlabels = {}

	@staticmethod
	def init():
		DTable.load_gamelistlabel()
		DTable.load_lobbylistlabels()

	@staticmethod
	def load_gamelistlabel():
		for lang in Lang.texts[Lang.gotoh_id]:
			DTable.gamelistlabels[lang] = collections.OrderedDict()
			DTable.gamelistlabels[lang]["name"] = Lang.get_from_lang(Lang.gotoh_id, "game", lang)
			DTable.gamelistlabels[lang]["players"] = Lang.get_from_lang(Lang.gotoh_id, "players", lang)
			DTable.gamelistlabels[lang]["args"] = Lang.get_from_lang(Lang.gotoh_id, "options", lang)
			DTable.gamelistlabels[lang]["devs"] = Lang.get_from_lang(Lang.gotoh_id, "devs", lang)

	@staticmethod
	def load_lobbylistlabels():
		for lang in Lang.texts[Lang.gotoh_id]:
			DTable.lobbylistlabels[lang] = collections.OrderedDict()
			DTable.lobbylistlabels[lang]["name"] = Lang.get_from_lang(Lang.gotoh_id, "game", lang)
			DTable.lobbylistlabels[lang]["players"] = Lang.get_from_lang(Lang.gotoh_id, "players", lang)
			DTable.lobbylistlabels[lang]["args"] = Lang.get_from_lang(Lang.gotoh_id, "options", lang)
			DTable.lobbylistlabels[lang]["host"] = Lang.get_from_lang(Lang.gotoh_id, "host", lang)


	# POSTULAT: length >= len(string)
	@staticmethod
	def fit_str(string, length, centered=False, fill=' '):
		if centered:
			space = length - len(string)
			halfspace = space//2
			res = halfspace*fill + string + halfspace*fill
			if space % 2 == 1:
				res += fill
		else:
			res = string + (length - len(string))*fill
		assert len(res) == length
		return res

	@staticmethod
	def get_table(labels, lines):
		bonus_spacing = 2
		# Find the longest label for each row
		maxlen = {}
		for (key, value) in labels.items():
			maxlen[key] = len(value) + bonus_spacing
		for line in lines:
			for (key, value) in line.items():
				print(value, ", len:", len(value))
				if maxlen[key] < len(value) + bonus_spacing:
					maxlen[key] = len(value) + bonus_spacing
		print("maxlens:", str(maxlen))
		# Build the discord message
		msg = "```"
		# Build the table header
		totalspace = 0
		for (key, value) in labels.items():
			msg += DTable.fit_str(value, maxlen[key], centered=True) + "║"
		msg += "\n"
		# Build the separation line
		for i, key in enumerate(labels):
			msg += DTable.fit_str("", maxlen[key], fill="═")
			if i < len(labels):
				msg += "╬"
		msg += "\n"
		# Fill the table
		for line in lines:
			for key in labels:
				print(line[key], ", len:", len(line[key]))
				msg += DTable.fit_str(line[key], maxlen[key]) + "║"
			msg += "\n"
		msg += "```"
		return msg

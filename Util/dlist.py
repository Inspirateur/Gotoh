class DList:
	@staticmethod
	def get(vect, effect="**"):
		it = iter(vect)
		msg_list = f"{effect}{next(it)}{effect}"
		for elem in it:
			msg_list += f", {effect}{elem}{effect}"
		return msg_list

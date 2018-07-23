# Class that deals with the "players" entry of meta files (ie: how many players a game accepts)
# There are 3 formats accepted: <max>, <min-max> and <min+>
class PC:
	# Checks if the Player Cap is written in a valid format
	@staticmethod
	def is_valid(pc):
		i = 0
		length = len(pc)
		while i < length and pc[i].isdecimal():
			i += 1
		if i == length:
			return True
		elif pc[i] == '-' and i < length-1:
			i += 1
			j = i
			while j < length and pc[j].isdecimal():
				j += 1
			if j == length:
				# Checks that min <= max in addition to checking the syntax
				return int(pc[:i]) <= int(pc[i:j])
		elif pc[i] == '+' and i == length-1:
			return True
		return False

	def __init__(self, pc):
		self.min = 0
		self.max = None
		self.rep = pc
		self.init_from_pn(pc)

	def __str__(self):
		return self.rep

	# ASSERT: the pc is correct
	def init_from_pn(self, pc):
		dash_i = pc.find("-")
		if dash_i != -1:
			self.min = int(pc[:dash_i])
			self.max = int(pc[dash_i+1:])
		else:
			if pc[-1] == "+":
				self.min = int(pc[:-1])
			else:
				self.min = int(pc)
				self.max = self.min

	def is_max(self, playernumber):
		if self.max is None:
			return False
		else:
			return playernumber == self.max

	def is_in_range(self, playernumber):
		if self.max is None:
			return playernumber >= self.min
		else:
			return self.min <= playernumber <= self.max
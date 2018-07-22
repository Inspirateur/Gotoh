import yaml
import os


class Prefix:
	servs = {}
	cwd = os.getcwd()

	@staticmethod
	def init():
		with open(f"{Prefix.cwd}\LangManagement\prefixs.txt", "r") as file:
			Prefix.servs = yaml.load(file)

	@staticmethod
	def set(serv, prefix):
		Prefix.servs[serv] = prefix
		with open(f"{Prefix.cwd}\LangManagement\prefixs.txt", "w") as file:
			yaml.dump(Prefix.servs, file, default_flow_style=False)

	@staticmethod
	def get(serv):
		if serv in Prefix.servs:
			return Prefix.servs[serv]
		else:
			return "."

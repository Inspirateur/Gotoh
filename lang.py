from discord.ext import commands
from LangManagement.lang_manager import Lang, DList
from LangManagement.prefix_manager import Prefix

class LangCog:
	def __init__(self, bot):
		self.bot = bot

	@commands.command(pass_context=True, brief="Set the command prefix for this server")
	async def prefix(self, ctx, *args):
		if len(args) == 0:
			await ctx.send(Lang.get_text("prefix", ctx))
		else:
			Prefix.set(ctx.message.guild.id, " ".join(args))
			await ctx.send(Lang.get_text("prefix_success", ctx))

	@commands.command(pass_context=True, brief="Set the main language of the channel")
	async def mainlang(self, ctx, *args):
		if len(args) == 0:
			await ctx.send(Lang.get_text("mainlang", ctx))
		else:
			language = "_".join(args)
			try:
				Lang.set_main_lang(ctx.message.channel.id, language)
				await ctx.send(Lang.get_text("mainlang_success", ctx).format(Lang.get_main_lang(ctx.message.channel.id)))
			except KeyError:
				await ctx.send(Lang.get_text("not_a_language", ctx).format(language))

	@commands.command(pass_context=True, aliases=["addlanguage"], brief="Add a language to the channel")
	async def addlang(self, ctx, *args):
		if len(args) == 0:
			await ctx.send(Lang.get_text("addlang", ctx))
		else:
			language = "_".join(args)
			try:
				Lang.add_lang(ctx.message.channel.id, language)
				await ctx.send(Lang.get_text("addlang_success", ctx).format(Lang.get_language(language)))
			except KeyError:
				await ctx.send(Lang.get_text("not_a_language", ctx).format(language))

	@commands.command(pass_context=True, alisases=["removelang", "rmlanguage", "removelanguage"], brief="Remove a language from the channel")
	async def rmlang(self, ctx, *args):
		if len(args) == 0:
			await ctx.send(Lang.get_text("rmlang", ctx))
		else:
			language = "_".join(args)
			try:
				Lang.rm_lang(ctx.message.channel.id, language)
				await ctx.send(Lang.get_text("rmlang_success", ctx).format(Lang.get_language(language)))
			except KeyError:
				await ctx.send(Lang.get_text("not_a_language", ctx).format(language))

	@commands.command(aliases=["language"], brief="List the channel's languages")
	async def lang(self, ctx):
		langlist = Lang.get_secondary_lang(ctx.message.channel.id)
		if len(langlist) == 0:
			msglist = Lang.get_text("none", ctx)
		else:
			msglist = DList.get(langlist)
		await ctx.send(Lang.get_text("lang", ctx).format(Lang.get_main_lang(ctx.message.channel.id), msglist))


def setup(bot):
	bot.add_cog(LangCog(bot))
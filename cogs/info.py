import discord
from discord.ext import commands

from helpers import CustomMember, CustomUser, CustomGuild
from main import MyClient, Context

class Info(commands.Cog):
	def __init__(self, client: MyClient):
		self.client = client

	@commands.hybrid_group(name="info", fallback="info-specs_fallback", description="info-specs_description")
	async def info(self, ctx: Context, user: discord.Member | discord.User | None = None):
		user = user or ctx.author

		if not ctx.guild:
			await ctx.send("info.user.not_member", member=CustomUser.from_user(user))
			return

		if isinstance(user, discord.Member):
			await ctx.send("info.user.member", member=CustomMember.from_member(user))
			return

		try:
			member = await ctx.guild.fetch_member(user.id)
			await ctx.send("info.user.member", member=CustomMember.from_member(member))
		except discord.NotFound:
			await ctx.send("info.user.not_member", member=CustomUser.from_user(user))

	@info.command(name="server", description="serverinfo-specs_description")
	@commands.guild_only()
	async def server(self, ctx):
		await ctx.send("info.server", server=CustomGuild.from_guild(ctx.guild))

async def setup(client: MyClient):
	await client.add_cog(Info(client))

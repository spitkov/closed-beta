import discord
from discord.ext import commands

from helpers.custom_args import *
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
	async def server(self, ctx: Context):
		await ctx.send("info.server", server=CustomGuild.from_guild(ctx.guild))

	@info.command(name="role", description="roleinfo-specs_description")
	@commands.guild_only()
	async def role(self, ctx: Context, role: Optional[discord.Role] = None):
		role = role or ctx.author.top_role
		if not role:
			raise commands.BadArgument("role")
		await ctx.send("info.role", role=CustomRole.from_role(role))

	@info.command(name="ip", description="ipinfo-specs_description")
	async def ip(self, ctx: Context, ip_addr: str):
		try:
			ip_json = await self.client.request(f"https://ipinfo.io/{ip_addr}/json")
		except RuntimeError:
			raise commands.BadArgument("ip")
		ip = IPAddress(ip_json)
		await ctx.send("info.ip", ip=ip)

	@info.command(name="bot", description="botinfo-specs_description")
	async def bot(self, ctx: Context):
		await ctx.send("info.bot", bot=BotInfo(self.client))


async def setup(client: MyClient):
	await client.add_cog(Info(client))

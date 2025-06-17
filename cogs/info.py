import asyncio

import discord
from discord import app_commands
import pypokedex
import requests
from discord.ext import commands
from emoji import EMOJI_DATA
from helpers.custom_args import *
from main import MyClient, Context
class Info(commands.Cog):
	def __init__(self, client: MyClient):
		self.client = client

	@commands.hybrid_group(name="info", description="info-specs_description")
	async def info(
		self,
		ctx: Context,
		argument:
			discord.User | discord.abc.GuildChannel | discord.Role | discord.Emoji | discord.PartialEmoji
	):
		if isinstance(argument, discord.User):
			await ctx.invoke(self.info.get_command("user"), argument)  # type: ignore
		elif isinstance(argument, discord.abc.GuildChannel):
			await ctx.invoke(self.info.get_command("channel"), argument)  # type: ignore
		elif isinstance(argument, discord.Role):
			await ctx.invoke(self.info.get_command("role"), argument)  # type: ignore
		elif isinstance(argument, (discord.Emoji, discord.PartialEmoji)):
			await ctx.invoke(self.info.get_command("emoji"), argument)  # type: ignore
		else:
			raise commands.BadArgument

	@info.command(name="user", fallback="userinfo-specs_fallback", description="userinfo-specs_description")
	async def user(self, ctx: Context, user: discord.Member | discord.User | None = None):
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

	@info.command(name="emoji", description="emojiinfo-specs_description")
	async def emoji(self, ctx: Context, emoji: str):
		try:
			emoji = await commands.EmojiConverter().convert(ctx, emoji)
		except commands.BadArgument:
			emoji = discord.PartialEmoji.from_str(emoji)
		if isinstance(emoji, discord.Emoji):
			await ctx.send("info.emoji.custom_emoji", emoji=CustomEmoji.from_emoji(emoji))
		elif isinstance(emoji, discord.PartialEmoji) and emoji.name in EMOJI_DATA:
			await ctx.send("info.emoji.unicode_emoji", emoji=CustomPartialEmoji.from_emoji(emoji))
		else:
			raise commands.BadArgument("emoji")

	@info.command(name="channel", description="channelinfo-specs_description")
	@commands.guild_only()
	async def channel(self, ctx: Context, channel: discord.abc.GuildChannel):
		if isinstance(channel, discord.TextChannel):
			await ctx.send("info.channel.text", channel=CustomTextChannel.from_channel(channel))
		elif isinstance(channel, discord.VoiceChannel):
			await ctx.send("info.channel.voice", channel=CustomVoiceChannel.from_channel(channel))
		elif isinstance(channel, discord.CategoryChannel):
			await ctx.send("info.channel.category", category=CustomCategoryChannel.from_category(channel))
		elif isinstance(channel, discord.ForumChannel):
			await ctx.send("info.channel.forum", channel=CustomForumChannel.from_channel(channel))
		elif isinstance(channel, discord.StageChannel):
			await ctx.send("info.channel.stage", channel=CustomStageChannel.from_channel(channel))
		else:
			raise commands.BadArgument("channel")

	@info.command(name="pokemon", description="pokeinfo-specs_description")
	async def pokemon(self, ctx: Context, pokemon_name: str):
		try:
			pokemon = await asyncio.get_event_loop().run_in_executor(None, lambda: pypokedex.get(name=pokemon_name))  # type: ignore
		except requests.HTTPError:
			raise commands.BadArgument("pokemon")
		pokemon.type = "\n".join(pokemon.types)
		pokemon.image = f"https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/official-artwork/{pokemon.dex}.png"

		await ctx.send("info.pokemon", pokemon=pokemon)

async def setup(client: MyClient):
	await client.add_cog(Info(client))

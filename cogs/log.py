import sys

from discord import app_commands

from helpers import *
from main import MyClient, Context

class LogCommands(commands.GroupCog, name="log"):
	def __init__(self, client: MyClient) -> None:
		self.client = client

	@commands.hybrid_group(name="log", fallback="log-specs_fallback", description="log-specs_description")
	@commands.has_permissions(manage_guild=True)
	@app_commands.checks.has_permissions(manage_guild=True)
	async def log_toggle(self, ctx: Context, state: Literal["on", "off"] = "on", channel: discord.TextChannel = None):
		is_on = state == "on"
		if is_on:
			if not channel:
				raise commands.MissingRequiredArgument(ctx.command.params["channel"])
			webhook = discord.utils.get(
				await channel.webhooks(), name=f"{ctx.me.display_name} - Log"
			) or await channel.create_webhook(
				name=f"{ctx.me.display_name} - Log", avatar=await ctx.me.avatar.read()
			)
		else:
			await self.client.db.execute("UPDATE log SET is_on = FALSE WHERE guild_id = $1", ctx.guild.id)
			await ctx.send("log.toggle.off")
			return

		await self.client.db.execute(
			"INSERT INTO log (guild_id, webhook, channel, is_on) VALUES ($1, $2, $3, $4)"
			" ON CONFLICT (guild_id) DO UPDATE"
			" SET webhook = excluded.webhook, channel = excluded.channel, is_on = excluded.is_on", ctx.guild.id,
			webhook.url, channel.id, is_on
		)
		await ctx.send(content="log.toggle.on")

	@log_toggle.group(name="module")
	async def log_module(self, ctx: Context):
		...

	@log_module.command(name="add")
	async def log_module_add(self, ctx: Context, module: str):
		if module == "all":
			await self.client.db.execute(
				"UPDATE log SET modules = DEFAULT WHERE guild_id = $1", ctx.guild.id
			)
		else:
			await self.client.db.execute(
				"UPDATE log SET modules = array_append(modules, $1) WHERE guild_id = $2",
				module, ctx.guild.id
			)

		await ctx.send("log.module.add")

	@log_module.command(name="remove")
	async def log_module_remove(self, ctx: Context, module: str):
		if module == "all":
			await self.client.db.execute(
				"UPDATE log SET modules = ARRAY[] WHERE guild_id = $1", ctx.guild.id
			)
		else:
			await self.client.db.execute(
				"UPDATE log SET modules = array_remove(modules, $1) WHERE guild_id = $2",
				module, ctx.guild.id
			)

		await ctx.send("log.module.add")

class LogListeners(commands.Cog):
	def __init__(self, client: MyClient) -> None:
		self.client = client

	# TODO:
	# 'on_automod_rule_create', 'on_automod_rule_update', 'on_automod_rule_delete', 'on_automod_action',
	# 'on_guild_channel_delete', 'on_guild_channel_create', 'on_guild_channel_update', 'on_guild_channel_pins_update',
	# 'on_guild_update', 'on_guild_emojis_update', 'on_guild_stickers_update', 'on_invite_create', 'on_invite_delete',
	# 'on_guild_integrations_update', 'on_webhooks_update', 'on_raw_integration_delete', 'on_member_join',
	# 'on_member_remove', 'on_member_update', 'on_member_ban', 'on_member_ban', 'on_member_unban', 'on_message_edit',
	# 'on_message_delete', 'on_bulk_message_delete', 'on_poll_vote_add', 'on_poll_vote_remove', 'on_reaction_add',
	# 'on_reaction_remove', 'on_reaction_clear', 'on_reaction_clear_emoji', 'on_guild_role_create',
	# 'on_guild_role_delete', 'on_scheduled_event_create', 'on_scheduled_event_delete', 'on_scheduled_event_update',
	# 'on_soundboard_sound_create', 'on_soundboard_sound_delete', 'on_soundboard_sound_update',
	# 'on_stage_instance_create', 'on_stage_instance_delete', 'on_stage_instance_update', 'on_thread_create',
	# 'on_thread_join', 'on_thread_update', 'on_thread_remove', 'on_thread_delete', 'on_thread_member_join',
	# 'on_thread_member_remove', 'on_voice_state_update'

	# DONE:

	async def get_webhook(self, guild_id: int) -> Optional[discord.Webhook]:
		webhook = await self.client.db.fetchval("SELECT webhook FROM log WHERE guild_id = $1", guild_id)
		if not webhook:
			return None
		return discord.Webhook.from_url(webhook, client=self.client)

	async def send_webhook(self, guild_id: int, key: Optional[str] = None, **kwargs):
		if not self.log_check(guild_id):
			return

		if not key:
			# automatically retreive the name of the function that calls this function and use it as the key
			key = f"log.{sys._getframe(1).f_code.co_name}"  # type: ignore

		webhook = await self.get_webhook(guild_id)
		if not webhook:
			return

		custom_response = CustomResponse(self.client)
		message: dict | str = await custom_response.get_message(key, self.client.get_guild(guild_id), **kwargs)
		if isinstance(message, dict):
			message.pop("delete_after", None)
			message.pop("ephemeral", None)
			await webhook.send(**message)
		else:
			await webhook.send(content=message)

	@overload
	async def log_check(self, guild: int):
		...

	@overload
	async def log_check(self, guild: discord.Guild):
		...

	async def log_check(self, guild: Union[int, discord.Guild]):
		if isinstance(guild, int):
			guild_id = guild
		elif isinstance(guild, discord.Guild):
			guild_id = guild.id
		return self.client.db.fetchval(
			f"SELECT is_on FROM log WHERE guild_id = $1 AND {sys._getframe(1).f_code.co_name} IN modules", # type: ignore
			guild_id
		)

	@commands.Cog.listener()
	async def on_automod_rule_create(self, rule: discord.AutoModRule):
		await self.send_webhook(rule.guild.id, rule=rule)

	@commands.Cog.listener()
	async def on_automod_rule_update(self, rule: discord.AutoModRule):
		await self.send_webhook(rule.guild.id, rule=rule)

	@commands.Cog.listener()
	async def on_message_delete(self, message: discord.Message):
		await self.send_webhook(message.guild.id, message=message)

	@commands.Cog.listener()
	async def on_message_edit(self, before: discord.Message, after: discord.Message):
		await self.send_webhook(before.guild.id, before=before, after=after)

async def setup(client: MyClient) -> None:
	await client.add_cog(LogCommands(client))
	await client.add_cog(LogListeners(client))

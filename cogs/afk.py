from time import perf_counter

import re
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import main
from helpers import custom_response, CustomUser
from helpers import regex
from main import MyClient


class AFK(commands.Cog):
    def __init__(self, client: MyClient):
        self.client: MyClient = client
        self.custom_response: custom_response.CustomResponse = custom_response.CustomResponse(client, "basic")

    @commands.Cog.listener("on_message")
    async def check_afk(self, message: discord.Message) -> None:
        """Listens to messages sent. If the author of the message is AFK, turn AFK off."""
        if not message.guild:
            return
        row = await self.client.db.fetchrow("SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2 AND state = TRUE", message.guild.id, message.author.id)
        if not row:
            return

        # Turn off AFK
        ctx = await self.client.get_context(message)
        await self.client.db.execute("UPDATE afk SET state = $1 WHERE user_id = $2 AND guild_id = $3", False,
                                     ctx.author.id, ctx.guild.id)
        try:
            await ctx.author.edit(nick=row["previous_nick"])
        except discord.Forbidden:
            pass
        await ctx.reply("afk.off")

        await self.client.process_commands(message)

    @commands.Cog.listener("on_message")
    async def answer_afk_reason(self, message: discord.Message) -> None:
        """Listens to messages. If exactly one mentioned user is AFK, reply with their AFK reason."""
        if message.author.bot or not message.guild:
            return

        if len(message.mentions) != 1:
            return

        mentioned_user = message.mentions[0]

        row = await self.client.db.fetchrow(
            "SELECT * FROM afk WHERE guild_id = $1 AND user_id = $2 AND state = TRUE",
            message.guild.id,
            mentioned_user.id
        )

        if not row:
            return

        ctx = await self.client.get_context(message)

        await ctx.reply("afk.reason", user=CustomUser.from_user(mentioned_user), reason=row["message"])
        await self.client.process_commands(message)

    @commands.hybrid_command(
        name="afk",
        description="afk_specs-description",
        usage="afk_specs-usage"
    )
    @app_commands.rename(
        reason="afk_specs-args-reason-name"
    )
    @app_commands.describe(
        reason="afk_specs-args-reason-description"
    )
    async def afk(self, ctx: main.Context, reason: Optional[str] = None):
        if not reason:
            reason = await self.custom_response("afk.dnd", ctx)

        if re.search(regex.DISCORD_INVITE, reason):
            return await ctx.send("afk.link")

        row = await self.client.db.fetchrow("SELECT * FROM afk WHERE user_id = $1 AND guild_id = $2", ctx.author.id,
                                            ctx.guild.id)
        if not row:
            await self.client.db.execute(
                "INSERT INTO afk (user_id, guild_id, message, state, previous_nick) VALUES($1, $2, $3, $4, $5)",
                ctx.author.id, ctx.guild.id, reason, True, ctx.author.display_name)
            try:
                await ctx.author.edit(
                    nick=(await self.custom_response("afk.name", ctx, nickname=ctx.author.display_name)))
            except discord.errors.Forbidden:
                pass
            return await ctx.send("afk.on")

        if row["state"]:
            # Turn off AFK
            await self.client.db.execute("UPDATE afk SET state = $1 WHERE user_id = $2 AND guild_id = $3", False,
                                         ctx.author.id, ctx.guild.id)
            try:
                await ctx.author.edit(nick=row["previous_nick"])
            except discord.Forbidden:
                pass
            return await ctx.send("afk.off")
        else:
            # Turn on AFK
            await self.client.db.execute(
                "UPDATE afk SET state = $1, message = $2, previous_nick = $3 WHERE user_id = $4 AND guild_id = $5",
                True, reason, ctx.author.display_name, ctx.author.id, ctx.guild.id)
            try:
                await ctx.author.edit(
                    nick=(await self.custom_response("afk.name", ctx, nickname=ctx.author.display_name)))
            except discord.Forbidden:
                pass
            return await ctx.send("afk.on")

async def setup(client: MyClient):
    await client.add_cog(AFK(client))
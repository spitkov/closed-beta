import discord
from discord.ext import commands, localization
from discord import app_commands
import logging
from typing import Literal, Optional

import main
from helpers import *

class Setup(commands.Cog):
    def __init__(self, client):
        self.client = client

    @commands.hybrid_command()
    @commands.has_permissions(administrator=True)
    @app_commands.rename(
        prefix="prefix",
        mention="mention"
    )
    @app_commands.describe(
        prefix="The prefix you want to set",
        mention="Whether to allow mentioning the bot as a prefix"
    )
    async def prefix(self, ctx: main.Context, prefix: str, mention: Optional[bool] = True):
        if len(prefix) > 10:
            return await ctx.send("setup.prefix.errors.long", prefix=prefix, limit=10)
        await self.client.db.execute("UPDATE guilds SET prefix = $1, mention = $2 WHERE guild_id = $3", prefix, mention, ctx.guild.id)
        await ctx.send("setup.prefix.set", prefix=prefix)

async def setup(client):
    await client.add_cog(Setup(client))
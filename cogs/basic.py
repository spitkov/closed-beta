from time import perf_counter

import re
from typing import Optional

import discord
from discord import app_commands
from discord.ext import commands

import main
from helpers import custom_response
from helpers import regex
from main import MyClient

class Basic(commands.Cog):
    def __init__(self, client: MyClient):
        self.client: MyClient = client
        self.custom_response: custom_response.CustomResponse = custom_response.CustomResponse(client, "basic")

    @commands.hybrid_command(
        name="ping",
        description="ping_specs-description"
    )
    async def ping(self, ctx: main.Context):
        # Database ping calculation
        database_start = perf_counter()
        await self.client.db.execute("SELECT guild_id FROM guilds WHERE guild_id = $1", ctx.guild.id)
        database = perf_counter() - database_start
        
        await ctx.send("ping", latency=float(self.client.latency), db=float(database))

async def setup(client: MyClient):
    await client.add_cog(Basic(client))
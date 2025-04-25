"""A helper for custom messages."""
import builtins
import os
import pprint

import discord
from discord.ext import localization
from discord.ext import commands
from typing import Union, Any
import random
import logging
from .custom_args import *


logger = logging.getLogger(__name__)

class CustomResponse:
    """A class to handle custom responses."""
    
    def __init__(self, client: discord.Client, name: Optional[str] = None) -> None:
        """A custom message instance.
        
        Parameters
        ----------
        client: `discord.Client`
            The client object with a `db` attribute.
        name: `str`
            The name of the cog that uses this class.
        """
        self.client = client
        self.name = name
    
    @staticmethod
    def convert_embeds(data: Any) -> Any:
        """Converts `data`'s embed (dict) or embeds (list) keys' values into a discord.Embed.
        
        This converts in a smart way: if there are both an `embed` and `embeds` key, `embed` will be merged into `embeds`.
        
        Parameters
        ----------
        data: `Any`
            The data that might contain an `embed` or an `embeds` key. Conversion is only performed if this is a `dict`.

        Raises
        ------
        ValueError
            If there are more than 10 embeds.
        
        Returns
        --------
        Any
            The original data, but with usable `discord.Embed`s.
        """
        if isinstance(data, dict) and (data.get("embed") or data.get("embeds")):
            if len(data["embeds"]) > 10:
                raise ValueError(f"The maximum number of embeds is 10. You have {len(data['embeds'])} embeds.")
            if data.get("embed") and not data.get("embeds"):
                data["embeds"] = [data["embed"]]

            data.pop("embed", None)
            
            if data.get("embeds"):
                data["embeds"] = [discord.Embed.from_dict(embed) for embed in data.get("embeds", [])]
        return data

    async def get_message(
        self,
        name: str,
        locale: Union[str, discord.Locale, discord.Guild, discord.Interaction, commands.Context],
        *,
        convert_embeds: bool = True,
        **kwargs: Any
    ) -> Union[Any, dict, str, list, int, float, bool]:
        """Gets a custom message from the database, or if not found, gets the default message.

        Parameters
        ----------
        name: str
            The name of the message.
        locale: Union[str, discord.Locale, discord.Guild, discord.Interaction, commands.Context]
            The locale to use or the context to derive it.
        convert_embeds: bool
            Whether to convert the embeds in the message to discord.Embeds.

        Returns
        -------
        Union[dict, str, list, int, float, bool]
            The message payload.
        """
        original = locale

        if isinstance(locale, (discord.Interaction, commands.Context)):
            locale = locale.guild.preferred_locale if (locale.guild and locale.guild.preferred_locale) else "en"
        elif isinstance(locale, discord.Guild):
            locale = locale.preferred_locale or "en"
        else:
            locale = str(locale)

        match original:
            case discord.Guild():
                guild_id = original.id
            case discord.Interaction() | commands.Context():
                guild_id = original.guild.id
            case _:
                guild_id = None

        custom_message: Union[dict, str] = "default_messages.json"

        context_formatting = {
            "author": CustomMember.from_user(original.author)
                if isinstance(original, (discord.Interaction, commands.Context)) else None,
            "guild": (CustomGuild.from_guild(original.guild)
                if isinstance(original, (discord.Interaction, commands.Context)) and hasattr(original, "guild")
                else CustomGuild.from_guild(original)
                if isinstance(original, discord.Guild) else None),
            "now": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        }

        payload = localization.Localization(custom_message, default_locale="en") \
            .localize(name, locale, **kwargs, random=r"{random}", **context_formatting)

        if isinstance(payload, dict):
            if random_value := payload.get("random"):
                payload = localization.Localization.format_strings(payload, random=random.choice(random_value))
            payload.pop("random", None)
            payload = self.convert_embeds(payload) if convert_embeds else payload

            if payload.get("reply"):
                payload["reference"] = original.message if isinstance(original, (discord.Interaction, commands.Context)) else None
            payload.pop("reply", None)

            if payload.get("ephemeral") or payload.get("delete_after"):
                if not isinstance(original, discord.Interaction):
                    payload.pop("ephemeral", None)
                else:
                    payload.pop("delete_after", None)
        return payload
    
    __call__ = get_message
"""Custom arguments to make user-specified responses easier to configure"""
import datetime
from dataclasses import dataclass, field
from typing import Union, Optional, Literal, Sequence

import discord

class CustomColor:
	"""Custom colors for formatting purposes.

	Operations
	----------
	`str(x)`: Returns the color in hex format.

	Examples
	--------
	>>> color = CustomColor(discord.Color.red())
	>>> color
	#FF0000

	>>> color.image
	'https://dummyimage.com/500x500/FF0000/000000&text=+'
	"""

	def __init__(self, color: Optional[discord.Color]):
		self.__color = color or discord.Color.light_grey()

	def __str__(self):
		return f'#{self.__color.value:0>6X}'  # '#RRGGBB' - '#AB12CD'

	@property
	def color(self) -> str:
		"""The color in hex format."""
		return str(self)

	colour = color

	@property
	def rgb(self) -> str:
		"""The color in RGB format."""
		colors = self.__color.to_rgb()
		return f"({colors[0]}, {colors[1]}, {colors[2]})"

	@property
	def image(self):
		return f'https://dummyimage.com/500x500/{self.__color.value:0>6X}/000000&text=+'

	pic = picture = image

	__repr__ = __str__

DatetimeFormat = Literal["time", "seconds", "date", "month", "short", "long", "relative", discord.utils.TimestampStyle]
"""The format to use for Discord timestamps."""

class Formattable:
	def __init__(self, data, *, style: discord.utils.TimestampStyle):
		"""A class that allows you to format a datetime object into a Discord timestamp.

		Parameters
		----------
		data: `FormatDateTime`
			The datetime object to format.
		"""
		self._parent_data = data
		self._style = style

	@property
	def value(self) -> str:
		return discord.utils.format_dt(self._parent_data.data, style=self._style)

	def __repr__(self):
		return self.value

	__str__ = __repr__

class FormatDateTime:
	"""Formats a datetime object into a dynamic Discord timestamp.

	You have to specify a default style, which will be used if no style is provided by the end user.
	This is needed because by passing this class as a value for a property, users can call it with or without brackets.
	So for example, ``created_at``, ``created_at()`` and ``created_at("long")`` will all work. The one without the
	brackets will always use the default style."""

	def __init__(self, data: datetime.datetime, default_style: discord.utils.TimestampStyle):
		self.data = data
		self.default_style = default_style

	@property
	def timestamp(self) -> str:
		return self.data.astimezone(datetime.timezone.utc).replace(tzinfo=None).strftime("%Y-%m-%dT%H:%M:%S.%fZ")

	@property
	def time(self) -> Formattable:
		"""Returns the hours and minutes of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").time
		22:57
		"""
		return Formattable(self, style="t")

	@property
	def seconds(self) -> Formattable:
		"""Returns the seconds of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").seconds
		22:57:43
		"""
		return Formattable(self, style="T")

	@property
	def date(self) -> Formattable:
		"""Returns the date of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").date
		2022-02-17
		"""
		return Formattable(self, style="D")

	@property
	def short(self) -> Formattable:
		"""Returns the short version of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").short
		17 Feb 2022
		"""
		return Formattable(self, style="f")

	@property
	def long(self) -> Formattable:
		"""Returns the long version of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").long
		Thursday, 17 February 2022
		"""
		return Formattable(self, style="F")

	@property
	def relative(self) -> Formattable:
		"""Returns the relative version of the timestamp.

		Examples
		--------
		>>> FormatDateTime(datetime.datetime.now(), "F").relative
		1 minute ago
		"""
		return Formattable(self, style="R")

	def __repr__(self) -> str:
		return Formattable(self, style=self.default_style).value

if __name__ == "__main__":
	pass

@dataclass
class CustomUser:
	_name: str = field(repr=False)
	id: int
	"""Returns the user's ID."""
	_discriminator: str = field(repr=False)
	global_name: str = field(repr=False)
	"""Returns the user's global display name. The hierarchy is as follows:
	
	1. ``name#discriminator`` if the user has a discriminator (only bots).
	2. ``global_name`` if the user has a global name.
	3. ``name`` if the user has neither a discriminator nor a global name."""
	display_name: str = field(repr=False)
	"""Returns the user's display name. This is the name that is shown in the server if they are a member.
	Otherwise, it is the same as ``global_name``."""
	bot: bool
	"""Returns whether or not the user is a Discord bot."""
	_color: Optional[CustomColor] = field(repr=False)
	_avatar: str = field(repr=False)
	_decoration: Optional[str] = field(repr=False)
	_banner: Optional[str] = field(repr=False)
	_created_at: datetime.datetime = field(repr=False)
	mention: str
	"""Returns a string that mentions the user."""

	@classmethod
	def from_user(cls, user: discord.User):
		"""Creates a ``CustomUser`` from a ``discord.User`` object."""
		return cls(
			_name=f"{user.name}#{user.discriminator}" if user.discriminator != "0" else user.name, id=user.id,
			_discriminator=user.discriminator,
			global_name=f"{user.name}#{user.discriminator}" if user.discriminator != "0" else (
					user.global_name or user.name), display_name=user.display_name or (
				f"{user.name}#{user.discriminator}" if user.discriminator != "0" else (user.global_name or user.name)),
			bot=user.bot, _color=CustomColor(user.accent_color), _avatar=user.display_avatar.url,
			_decoration=user.avatar_decoration.url if user.avatar_decoration else "",
			_banner=user.banner.url if user.banner else CustomColor(user.accent_color).image,
			_created_at=user.created_at, mention=user.mention
		)

	@property
	def name(self) -> str:
		"""Returns the username of the user."""
		return self._name

	user_name = user = username = name

	@property
	def discriminator(self) -> str:
		"""Returns the discriminator of the user. This is a legacy concept that only applies to bots."""
		return self._discriminator

	tag = discriminator

	@property
	def color(self) -> CustomColor:
		"""Returns the user's accent color."""
		return self._color

	colour = color

	@property
	def avatar(self) -> str:
		"""Returns the user's avatar URL."""
		return self._avatar

	icon = avatar

	@property
	def created_at(self):
		"""Returns the date the user was created as a Discord timestamp. You can call this with or without brackets.
		If you call it with braces you can pass a ``DatetimeFormat`` to format the timestamp."""
		return FormatDateTime(self._created_at, "F")

	created = created_at

	def __str__(self):
		return self.global_name

	def __int__(self):
		return self.id

@dataclass
class CustomMember(CustomUser):
	_nickname: Optional[str] = field(repr=False)
	_color: Optional[CustomColor] = field(repr=False)
	_accent_color: Optional[CustomColor] = field(repr=False)
	_joined_at: datetime.datetime = field(repr=False)
	_roles: list[discord.Role] = field(repr=False)

	@classmethod
	def from_user(cls, member: discord.Member):
		return cls(
			_name=f"{member.name}#{member.discriminator}" if member.discriminator else member.name, id=member.id,
			_discriminator=member.discriminator,
			global_name=f"{member.name}#{member.discriminator}" if member.discriminator else (
					member.global_name or member.name), display_name=member.display_name, _nickname=member.nick,
			bot=member.bot, _color=CustomColor(member.color), _accent_color=CustomColor(member.accent_color),
			_avatar=member.display_avatar.url,
			_decoration=member.avatar_decoration.url if member.avatar_decoration else None,
			_banner=member.avatar_decoration.url if member.banner else None, _created_at=member.created_at,
			_joined_at=member.joined_at, _roles=member.roles, mention=member.mention
		)

	@property
	def color(self) -> CustomColor:
		"""Returns the member's chat display color, aka. the color of their top role."""
		return self._color

	@property
	def joined_at(self):
		"""Returns the date the member joined the server as a Discord timestamp. You can call this with or without
		brackets. If you call it with braces you can pass a ``DatetimeFormat`` to format the timestamp."""
		return FormatDateTime(self._joined_at, "F")

	joined = joined_at

	@property
	def roles(self) -> str:
		"""Returns the """
		self._roles.pop(0)
		return ', '.join([role.mention for role in self._roles])

	@property
	def roles_reverse(self) -> str:
		self._roles.pop(0)
		return ', '.join([role.mention for role in reversed(self._roles)])

	def __str__(self):
		return self.display_name

@dataclass
class CustomRole:
	name: str
	"""Returns the role's name."""
	id: int
	"""Returns the role's ID."""
	hoist: bool
	"""Returns whether or not the role is hoisted (aka. shown seperately from other members)."""
	position: int
	"""Returns the role's position in the hierarchy."""
	managed: bool
	"""Returns whether or not the role is managed by an integration, such as Twitch or Patreon."""
	mentionable: bool
	"""Returns whether or not the role is mentionable by everyone."""
	_default: bool = field(repr=False)
	_bot: bool = field(repr=False)
	_boost: bool = field(repr=False)
	_integration: bool = field(repr=False)
	_assignable: bool = field(repr=False)
	_color: Optional[CustomColor] = field(repr=False)
	icon: str = field(repr=False)
	"""Returns the role's icon URL, or an emoji, if the role has one. This is only available for guilds that are
	boosted to at least level 2."""
	_created_at: datetime.datetime = field(repr=False)
	mention: str
	"""Returns a string that mentions the role."""
	_members: list[discord.Member] = field(repr=False)
	_purchaseable: bool = field(repr=False)

	@classmethod
	def from_role(cls, role: discord.Role):
		return cls(
			name=role.name, id=role.id, hoist=role.hoist, position=role.position, managed=role.managed,
			mentionable=role.mentionable, _default=role.is_default(), _bot=role.is_bot_managed(),
			_boost=role.is_premium_subscriber(), _integration=role.is_integration(), _assignable=role.is_assignable(),
			_color=CustomColor(role.color),
			icon=role.display_icon.url or role.display_icon if role.display_icon else None, _created_at=role.created_at,
			mention=role.mention, _members=role.members,
			_purchaseable=role.tags.is_available_for_purchase() if role.tags else False
		)

	@property
	def everyone(self) -> bool:
		"""Returns whether or not the role is the everyone role."""
		return self._default

	default = is_default = everyone

	@property
	def bot(self) -> bool:
		"""Returns whether or not the role is managed by a bot."""
		return self._bot

	is_bot = is_bot_managed = bot

	@property
	def boost(self) -> bool:
		"""Returns whether or not the role is a boost role."""
		return self._boost

	is_boost = is_premium_subscriber = boost

	@property
	def integration(self) -> bool:
		"""Returns whether or not the role is managed by an integration."""
		return self._integration

	is_integration_managed = integration_managed = is_integration = integration

	@property
	def assignable(self) -> bool:
		"""Returns whether or not the role is assignable by the bot itself."""
		return self._assignable

	allowed = is_assignable = assignable

	@property
	def purchaseable(self) -> bool:
		"""Returns whether or not the role is purchaseable."""
		return self._purchaseable

	buy = buyable = is_buyable = purchase = is_purchaseable = purchaseable

	@property
	def color(self) -> CustomColor:
		"""Returns the role's color."""
		return CustomColor(self._color)

	colour = color

	@property
	def created_at(self):
		"""Returns the date the role was created as a Discord timestamp. You can call this with or without brackets.
		If you call it with braces you can pass a ``DatetimeFormat`` to format the timestamp."""
		return FormatDateTime(self._created_at, "F")

	created = created_at

	def __str__(self):
		return self.name

	def __int__(self):
		return self.id

@dataclass
class CustomGuild:
	name: str
	"""Returns the guild's name."""
	id: int
	"""Returns the guild's ID."""
	_icon: Optional[discord.Asset] = field(repr=False)
	_banner: Optional[discord.Asset] = field(repr=False)
	_splash: Optional[discord.Asset] = field(repr=False)
	_discovery_splash: Optional[discord.Asset] = field(repr=False)
	description: Optional[str] = field(repr=False)
	"""Returns the guild's description, if it has one."""
	members: Optional[int] = field(repr=False)
	"""Returns the number of members in the guild."""
	owner: discord.Member = field(repr=False)
	"""Returns the guild's owner."""
	boosts: int = field(repr=False)
	"""Returns how many boosts the guild has."""
	_created_at: datetime.datetime = field(repr=False)
	_verification_level: discord.VerificationLevel = field(repr=False)
	_default_notifications: discord.NotificationLevel = field(repr=False)
	_explicit_content_filter: discord.ContentFilter = field(repr=False)
	_mfa_level: discord.MFALevel = field(repr=False)
	_system_channel: Optional[discord.TextChannel] = field(repr=False)
	_rules_channel: Optional[discord.TextChannel] = field(repr=False)
	_public_updates_channel: Optional[discord.TextChannel] = field(repr=False)
	_preferred_locale: discord.Locale = field(repr=False)
	_afk_channel: Optional[Union[discord.VoiceChannel, discord.StageChannel]] = field(repr=False)
	"""Returns the guild's AFK channel."""
	_afk_timeout: int = field(repr=False)
	"""Returns the guild's AFK timeout."""
	_vanity_url: Optional[str] = field(repr=False)
	_premium_tier: int = field(repr=False)
	_premium_subscribers: list[discord.Member] = field(repr=False)
	_premium_subscriber_role: Optional[discord.Role] = field(repr=False)
	_nsfw_level: discord.NSFWLevel = field(repr=False)
	_channels: Sequence[discord.abc.GuildChannel] = field(repr=False)
	_voice_channels: list[discord.VoiceChannel] = field(repr=False)
	_stage_channels: list[discord.StageChannel] = field(repr=False)
	_text_channels: list[discord.TextChannel] = field(repr=False)
	_categories: list[discord.CategoryChannel] = field(repr=False)
	_forums: list[discord.ForumChannel] = field(repr=False)
	_threads: Sequence[discord.Thread] = field(repr=False)
	_roles: Sequence[discord.Role] = field(repr=False)
	_emojis: tuple[discord.Emoji, ...] = field(repr=False)
	emoji_limit: int = field(repr=False)
	"""Returns the max amount of emojis the guild can have."""
	_stickers: tuple[discord.GuildSticker, ...] = field(repr=False)
	_sticker_limit: int = field(repr=False)
	_bitrate_limit: float = field(repr=False)
	_filesize_limit: int = field(repr=False)
	_scheduled_events: Sequence[discord.ScheduledEvent] = field(repr=False)
	_shard_id: int = field(repr=False)

	@classmethod
	def from_guild(cls, guild: discord.Guild):
		return cls(
			name=guild.name, id=guild.id, _icon=guild.icon, _banner=guild.banner, _splash=guild.splash,
			_discovery_splash=guild.discovery_splash, description=guild.description, members=guild.member_count,
			owner=guild.owner, boosts=guild.premium_subscription_count, _created_at=guild.created_at,
			_verification_level=guild.verification_level, _default_notifications=guild.default_notifications,
			_explicit_content_filter=guild.explicit_content_filter, _mfa_level=guild.mfa_level,
			_system_channel=guild.system_channel, _rules_channel=guild.rules_channel,
			_public_updates_channel=guild.public_updates_channel, _preferred_locale=guild.preferred_locale,
			_afk_channel=guild.afk_channel, _afk_timeout=guild.afk_timeout, _vanity_url=guild.vanity_url,
			_premium_tier=guild.premium_tier, _premium_subscribers=guild.premium_subscribers,
			_premium_subscriber_role=guild.premium_subscriber_role, _nsfw_level=guild.nsfw_level,
			_channels=guild.channels, _voice_channels=guild.voice_channels, _stage_channels=guild.stage_channels,
			_text_channels=guild.text_channels, _categories=guild.categories, _forums=guild.forums,
			_threads=guild.threads, _roles=guild.roles, _emojis=guild.emojis, emoji_limit=guild.emoji_limit,
			_stickers=guild.stickers, _sticker_limit=guild.sticker_limit, _bitrate_limit=guild.bitrate_limit,
			_filesize_limit=guild.filesize_limit, _scheduled_events=guild.scheduled_events, _shard_id=guild.shard_id
		)

	@property
	def icon(self) -> Optional[str]:
		"""Returns the guild's icon URL."""
		return self._icon.url if self._icon else ""

	@property
	def banner(self) -> Optional[str]:
		"""Returns the guild's banner URL."""
		return self._banner.url if self._banner else ""

	@property
	def splash(self) -> Optional[str]:
		"""Returns the guild's splash URL."""
		return self._splash.url if self._splash else ""

	@property
	def discovery_splash(self) -> Optional[str]:
		"""Returns the guild's discovery splash URL."""
		return self._discovery_splash.url if self._discovery_splash else ""

	@property
	def created_at(self):
		"""Returns the date the guild was created as a Discord timestamp. You can call this with or without brackets.
		If you call it with braces you can pass a ``DatetimeFormat`` to format the timestamp."""
		return FormatDateTime(self._created_at, "F")

	created = created_at

	@property
	def verification_level(self) -> str:
		"""Returns the guild's verification level."""
		mapping = { discord.VerificationLevel.none: r"{verification.none}",
			discord.VerificationLevel.low: r"{verification.low}",
			discord.VerificationLevel.medium: r"{verification.medium}",
			discord.VerificationLevel.high: r"{verification.high}",
			discord.VerificationLevel.highest: r"{verification.highest}" }
		return mapping.get(mapping)

	@property
	def default_notifications(self) -> str:
		"""Returns the guild's default notification level."""
		mapping = { discord.NotificationLevel.all_messages: r"{notification.all_messages}",
			discord.NotificationLevel.only_mentions: r"{notification.only_mentions}" }
		return mapping.get(mapping)

	@property
	def explicit_content_filter(self) -> str:
		"""Returns the guild's explicit content filter level."""
		mapping = { discord.ContentFilter.disabled: r"{content_filter.disabled}",
			discord.ContentFilter.no_role: r"{content_filter.no_role}",
			discord.ContentFilter.all_members: r"{content_filter.all_members}" }
		return mapping.get(mapping)

	@property
	def mfa_level(self) -> str:
		"""Returns the guild's MFA level."""
		mapping = { discord.MFALevel.disabled: r"{mfa.disabled}", discord.MFALevel.require_2fa: r"{mfa.require_2fa}", }
		return mapping.get(mapping)

	@property
	def system_channel(self) -> str:
		"""Returns the guild's system channel."""
		return self._system_channel.mention

	@property
	def rules_channel(self) -> str:
		"""Returns the guild's rules channel."""
		return self._rules_channel.mention

	@property
	def public_updates_channel(self) -> str:
		"""Returns the guild's public updates channel."""
		return self._public_updates_channel.mention

	@property
	def preferred_locale(self) -> str:
		"""Returns the guild's preferred locale."""
		return str(self._preferred_locale)

	locale = language = preferred_locale

	@property
	def afk_channel(self) -> str:
		"""Returns the guild's AFK channel."""
		return self._afk_channel.mention

	@property
	def vanity_url(self) -> str:
		"""Returns the guild's vanity URL."""
		return self._vanity_url

	@property
	def premium_tier(self) -> int:
		"""Returns the guild's premium tier."""
		return self._premium_tier

	boost_tier = premium_tier

	@property
	def premium_subscribers(self) -> int:
		"""Returns the guild's premium subscribers."""
		return len(self._premium_subscribers)

	boosters = premium_subscribers

	@property
	def premium_subscriber_role(self) -> str:
		"""Returns the guild's premium subscriber role."""
		return self._premium_subscriber_role.mention

	boost_role = premium_subscriber_role

	@property
	def nsfw_level(self) -> str:
		"""Returns the guild's NSFW level."""
		mapping = { discord.NSFWLevel.default: r"{nsfw.default}", discord.NSFWLevel.explicit: r"{nsfw.explicit}",
			discord.NSFWLevel.safe: r"{nsfw.safe}", discord.NSFWLevel.age_restricted: r"{nsfw.age_restricted}" }
		return mapping.get(mapping)

	@property
	def channels(self) -> int:
		"""Returns the number of channels in the guild."""
		return len(self._channels)

	@property
	def voice_channels(self) -> int:
		"""Returns the number of voice channels in the guild."""
		return len(self._voice_channels)

	@property
	def stage_channels(self) -> int:
		"""Returns the number of stage channels in the guild."""
		return len(self._stage_channels)

	@property
	def text_channels(self) -> int:
		"""Returns the number of text channels in the guild."""
		return len(self._text_channels)

	@property
	def categories(self) -> int:
		"""Returns the number of categories in the guild."""
		return len(self._categories)

	@property
	def forums(self) -> int:
		"""Returns the number of forums in the guild."""
		return len(self._forums)

	@property
	def threads(self) -> int:
		"""Returns the number of threads in the guild."""
		return len(self._threads)

	@property
	def roles(self) -> int:
		"""Returns the number of roles in the guild."""
		return len(self._roles)

	@property
	def emojis(self) -> int:
		"""Returns the number of emojis in the guild."""
		return len(self._emojis)

	@property
	def stickers(self) -> int:
		"""Returns the number of stickers in the guild."""
		return len(self._stickers)

	@property
	def bitrate_limit(self) -> float:
		"""Returns the bitrate limit of the guild."""
		return self._bitrate_limit

	bitrate = max_bitrate = bitrate_limit

	@property
	def filesize_limit(self) -> int:
		"""Returns the filesize limit of the guild in megabytes."""
		return int(self._filesize_limit / 1048576)  # Converts bytes to megabytes

	file_limit = file_size = max_file_size = filesize_limit

	@property
	def shard_id(self) -> int:
		"""Returns the shard ID of the guild."""
		return self._shard_id

	shard = shard_id

	@property
	def scheduled_events(self) -> int:
		"""Returns the number of scheduled events in the guild."""
		return len(self._scheduled_events)

	def __str__(self):
		return self.name

	def __int__(self):
		return self.id

	def __len__(self):
		return self.members

class CustomIP:
	def __init__(self, data: dict[str, str]):
		self._data = data

		for key in ['hostname', 'city', 'postal', 'region', 'country', 'org', 'timezone', 'loc']:
			if key not in self._data:
				self._data[key] = '❌'

	@property
	def ip(self) -> str:
		return self._data['ip']

	@property
	def code(self) -> str:
		return self._data['country']

	country = code

	@property
	def hostname(self) -> str:
		return self._data['hostname']

	@property
	def city(self) -> str:
		return self._data['city']

	@property
	def region(self) -> str:
		return self._data['region']

	@property
	def postal(self) -> str:
		return self._data['postal']

	@property
	def timezone(self) -> str:
		return self._data['timezone']

	@property
	def organization(self) -> str:
		return self._data['org']

	org = organization

	@property
	def loc(self) -> str:
		return self._data['loc']

class CustomBOT:
	def __init__(self, data: dict[str, str]):
		self._data = data

	@property
	def host_name(self) -> str:
		return self._data['host_name']

	@property
	def host_contact(self) -> str:
		return self._data['host_contact']

	@property
	def memory_usage(self) -> str:
		return self._data['memory_usage']

	@property
	def memory_str(self) -> str:
		return self._data['memory_str']

	@property
	def disk_usage(self) -> str:
		return self._data['disk_usage']

	@property
	def boot_time(self) -> str:
		return self._data['boot_time']

	@property
	def network_io(self) -> str:
		return self._data['network_io']

	@property
	def cpu_percent(self) -> str:
		return self._data['cpu_percent']

	@property
	def cpu_count(self) -> str:
		return self._data['cpu_count']

	@property
	def cpu_name(self) -> str:
		return self._data['cpu_name']

	@property
	def cpu_frequency(self) -> str:
		return self._data['cpu_frequency']

	@property
	def os_name(self) -> str:
		return self._data['os_name']

	@property
	def programming_library(self) -> str:
		return self._data['programming_library']

import discord
from discord.ext import commands

ROLE_MESSAGE_ID = 1463250512949416060
ROLE_CHANNEL_ID = 1463249293853982842


ROLE_EMOJI_MAP = {
    "🏛️": "Builder",
    "💻": "Modder",
    "🏕️": "Servers",
    "📰": "News"
}

class RoleCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        if payload.channel_id != ROLE_CHANNEL_ID:
            return

        if payload.message_id != ROLE_MESSAGE_ID:
            return

        if payload.user_id == self.bot.user.id:
            return

        emoji = str(payload.emoji)
        if emoji not in ROLE_EMOJI_MAP:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = discord.utils.get(guild.roles, name=ROLE_EMOJI_MAP[emoji])
        if role:
            await member.add_roles(role, reason="Emoji Role Add")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):

        if payload.channel_id != ROLE_CHANNEL_ID:
            return

        if payload.message_id != ROLE_MESSAGE_ID:
            return

        emoji = str(payload.emoji)
        if emoji not in ROLE_EMOJI_MAP:
            return

        guild = self.bot.get_guild(payload.guild_id)
        if not guild:
            return

        member = guild.get_member(payload.user_id)
        if not member:
            return

        role = discord.utils.get(guild.roles, name=ROLE_EMOJI_MAP[emoji])
        if role:
            await member.remove_roles(role, reason="Emoji Role Remove")

async def setup(bot):
    await bot.add_cog(RoleCog(bot))
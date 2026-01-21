import discord
from discord.ext import commands, tasks
import aiohttp
import json
from pathlib import Path
from datetime import datetime

GUILD_ID = 1463239132129136893
ANNOUNCE_CHANNEL_ID = 1463265703887896777
NEWS_CHANNEL_ID = 1463259777286144032
STATE_FILE = Path("data/hytale_state.json")

ROLE_MAP = {
    "builder": "Builder",
    "modder": "Modder",
    "servers": "Servers",
    "news": "News",
    "": "@everyone"
}



class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

        if not STATE_FILE.exists():
            STATE_FILE.parent.mkdir(exist_ok=True)
            STATE_FILE.write_text(json.dumps({"last_post_id": None}))

    @commands.Cog.listener()
    async def on_ready(self):
        if not self.check_updates.is_running():
            self.check_updates.start()

    def load_state(self):
        return json.loads(STATE_FILE.read_text())

    def save_state(self, state):
        STATE_FILE.write_text(json.dumps(state, indent=2))

    @tasks.loop(minutes=10)
    async def check_updates(self):

        headers = {
            "Accept": "application/json",
            "Accept-Language": "en",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
        }

        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(
                    "https://hytale.com/api/blog/post/published?limit=1"
            ) as resp:
                if resp.status != 200:
                    return

                data = await resp.json()

        if not data:
            return

        latest = data[0]


        try:
            slug = latest["slug"]
            title = latest["title"]
            published_at = latest["publishedAt"]
        except KeyError:
            return


        dt = datetime.fromisoformat(published_at.replace("Z", ""))
        link = f"https://hytale.com/news/{dt.year}/{dt.month}/{slug}"


        state = self.load_state()
        if state.get("last_post_id") == slug:
            return

        state["last_post_id"] = slug
        self.save_state(state)


        guild = self.bot.get_guild(GUILD_ID)
        if not guild:
            return

        role = discord.utils.get(guild.roles, name=ROLE_MAP["news"])
        channel = guild.get_channel(NEWS_CHANNEL_ID)

        if not role or not channel:
            return

        embed = discord.Embed(
            title=title,
            description="Der er netop udkommet et nyt blogpost fra Hytale.",
            url=link,
            colour=discord.Colour.green()
        )
        embed.set_footer(text="Hytale Danmark")

        await channel.send(content=role.mention, embed=embed)

    @commands.command(name="announce")
    @commands.has_permissions(manage_messages=True)
    async def announce(self, ctx, role_key: str, *, message: str):
            role_key = role_key.lower()

            if role_key not in ROLE_MAP:
                await ctx.send("Ugyldig rolle! Brug: builder, modder, servers, news eller everyone")
                return

            guild = ctx.guild
            role_name = ROLE_MAP[role_key]
            role = discord.utils.get(guild.roles, name=role_name)

            if not role:
                await ctx.send(f"Rollen '{role_name}' findes ikke")
                return

            channel = ctx.channel
            if not channel:
                await ctx.send("Hvem har slettet announcement kanalen??")
                return

            embed = discord.Embed(
                description=message,
                colour=discord.Colour.blue()
            )
            embed.set_footer(text="Hytale Danmark")

            await channel.send(
                content=role.mention,
                embed=embed
            )

            await ctx.message.delete()

async def setup(bot):
    await bot.add_cog(UpdateCog(bot))

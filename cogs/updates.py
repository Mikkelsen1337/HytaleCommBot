import discord
from discord.ext import commands, tasks
import aiohttp
import json
from pathlib import Path
from bs4 import BeautifulSoup

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

Hytale_News_URL = "https://hytale.com/news"

class UpdateCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.check_updates.start()

        if not STATE_FILE.exists():
            STATE_FILE.parent.mkdir(exist_ok=True)
            STATE_FILE.write_text(json.dumps({"last_post_id": None}))

    def load_state(self):
        return json.loads(STATE_FILE.read_text())

    def save_state(self, state):
        STATE_FILE.write_text(json.dumps(state, indent=2))

    @tasks.loop(minutes=10)
    async def check_updates(self):
        await self.bot.wait_until_ready()

        async with aiohttp.ClientSession() as session:
            async with session.get(Hytale_News_URL) as resp:
                if resp.status != 200:
                    return

                html = await resp.text()


        soup = BeautifulSoup(html, "html.parser")

        first_article = soup.select_one("a[href^='/news/']")
        if not first_article:
            return

        link = "https://hytale.com" + first_article.get["href"]
        title = first_article.get_text(strip=True)

        state = self.load_state()
        if state.get("last_post_id") == link:
            return

        state["last_post_id"] = link
        self.save_state(state)

        guild = self.bot.guilds[0]
        role = discord.utils.get(guild.roles, name=ROLE_MAP["news"])
        channel = guild.get_channel(NEWS_CHANNEL_ID)

        if not role or not channel:
            return

        embed = discord.Embed(
            title=title or "Ny Hytale Opdatering",
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

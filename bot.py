import discord
from discord.ext import commands
import os
from dotenv import load_dotenv

load_dotenv()

INTENTS = discord.Intents.default()
INTENTS.members = True
INTENTS.message_content = True
INTENTS.reactions = True

bot = commands.Bot(command_prefix="!", intents=INTENTS)

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")

async def load_cogs():
    for cog in ["roles", "updates"]:
        await bot.load_extension(f"cogs.{cog}")

@bot.event
async def setup_hook():
    await load_cogs()

bot.setup_hook = setup_hook

bot.run(os.getenv("DISCORD_TOKEN"))
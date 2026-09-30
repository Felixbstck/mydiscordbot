import discord
from discord import app_commands
from discord.ext import commands, tasks
from dotenv import load_dotenv
import os

# Load token
load_dotenv()

TOKEN = os.getenv("TOKEN")
WHITELIST = ["youtube", "reddit", "twitter"]

def parse_ids(value: str) -> set[int]:
    return {int(x) for x in value.split(",") if x.strip()}

OWNER_ID = int(os.getenv("OWNER_ID", 0))
EXEMPT_USER_IDS = parse_ids(os.getenv("EXEMPT_USER_IDS", ""))
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", 0))

client = commands.Bot(command_prefix = '.', intents=discord.Intents.all())
client.remove_command('help')


@client.event
async def on_ready():
    activity = discord.Game(name='Vibin')
    await client.change_presence(status=discord.Status.online, activity=activity)
    synced = await client.tree.sync()
    print(f"Synced {len(synced)} commands")
    print("Bot is ready")
    
@client.event

async def setup_hook():
    await client.load_extension("cogs.helpcommand")
    await client.load_extension("cogs.discordusers")
    print("loaded cogs successfully")

@client.event

async def on_message(message):
    author = message.author
    content = message.content
        
    await client.process_commands(message)

    if author.id in EXEMPT_USER_IDS or author.bot:
        return

    is_invite = "discord.gg/" in content
    is_blocked_link = "https://" in content and not any(s in content for s in WHITELIST)

    if not (is_invite or is_blocked_link):
        return

    await message.delete()

    embed = discord.Embed(
        colour = discord.Colour.blurple(),
        description = f"**Message sent by {author.mention} deleted in {message.channel.mention}**\nContents: {content}",
    )
    channel = client.get_channel(LOG_CHANNEL_ID)
    embed.set_author(name=f'{str(author)}', icon_url = author.display_avatar.url)
    await channel.send(embed=embed)
    await channel.send(f"<@{OWNER_ID}> you may need to ban this member")

        

@client.event

async def on_command_error(ctx, error):
    if type(error) == commands.CommandNotFound:
        return
    raise error


@client.command()
async def ping(ctx):

    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title='Pong',
        description='Ping pong!'
        )
    await ctx.send(embed=embed)


@client.command()

async def pong(ctx):
    embed = discord.Embed(
        colour = discord.Colour.orange(),
        title='Ping!',
        description="Wait that's not how it works!"
        )
    await ctx.send(embed=embed)


@client.command()

async def echo(ctx, *args):
    if any('discord.gg/' in arg for arg in args):
        return
    
    await ctx.send('{}'.format(' '.join(args)))

    
client.run(TOKEN)
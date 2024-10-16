import discord
from discord.ext import commands
import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get sensitive values from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
FORGE_API_KEY = os.getenv('FORGE_API_KEY')

# TODO
# Define trusted users' Discord IDs
TRUSTED_USERS = [
    135630872652021761, # Dark
    89850959345246208, # Tanis
    279459304023654400, # Sarhara
    254640527369175041 # ElPresidente
]  # Replace with actual trusted user IDs

# Create the bot with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)



# Function to check status of all games
def get_world_status():
    headers = {
        'Access-Key': FORGE_API_KEY
    }
    try:
        response = requests.get('https://forge-vtt.com/api/game/status', headers=headers)
        if response.status_code == 200:
            return response.json()  # Return the list of games with status
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

# Function to start a specific game by slug
def start_world(game_slug):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post('https://forge-vtt.com/api/game/start', headers=headers, json={'game': game_slug})
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to stop a specific game by slug
def stop_world(game_slug):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'Content-Type': 'application/json'
    }
    try:
        response = requests.post('https://forge-vtt.com/api/game/stop', headers=headers, json={'game': game_slug})
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False

# Function to idle a specific game by slug
def idle_world(game_slug, force=False, world=None):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'Content-Type': 'application/json'
    }
    body = {'game': game_slug}
    if force:
        body['force'] = True
    if world:
        body['world'] = world
    try:
        response = requests.post('https://forge-vtt.com/api/game/idle', headers=headers, json=body)
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        return False


@bot.command(name='ping')
async def ping(ctx):
    await ctx.send('Pong!')

# Bot command: Check world statuses
@bot.command(name='world-status')
async def world_status(ctx):
    worlds = get_world_status()
    if worlds:
        status_report = '\n'.join([f"World: {world['name']}, Status: {'Online' if world['active'] else 'Offline'}" for world in worlds])
        await ctx.send(f"World Status:\n{status_report}")
    else:
        await ctx.send("Error retrieving world statuses.")

# Bot command: Start a world
@bot.command(name='world-on')
async def world_on(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if start_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now online.")
    else:
        await ctx.send("Failed to start the world. Please check the game slug or your permissions.")

# Bot command: Stop a world
@bot.command(name='world-off')
async def world_off(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if stop_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now offline.")
    else:
        await ctx.send("Failed to stop the world. Please check the game slug or your permissions.")

# Bot command: Idle a world
@bot.command(name='world-idle')
async def world_idle(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if idle_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now idle.")
    else:
        await ctx.send("Failed to idle the world. Please check the game slug or your permissions.")


# will only respond to users, not other bots
@bot.event
async def on_message(message):
    if message.author.bot:  # Ignore messages from other bots
        return
    await bot.process_commands(message)


@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {str(error)}")
    print(f"Error: {error}")

# Run the bot using the token from the .env file
bot.run(DISCORD_BOT_TOKEN)
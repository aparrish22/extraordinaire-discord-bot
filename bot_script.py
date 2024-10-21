import discord
from discord.ext import commands
import requests
import json
import os
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Get sensitive values from environment variables
DISCORD_BOT_TOKEN = os.getenv('DISCORD_BOT_TOKEN')
FORGE_API_KEY = os.getenv('FORGE_API_KEY')

# Define trusted users' Discord IDs
TRUSTED_USERS = [
    135630872652021761, # Dark
    89850959345246208, # Tanis
    279459304023654400, # Sarhara
    254640527369175041 # ElPresidente
]  # Replace with actual trusted user IDs

# dictionary to track world statuses (online/offline)
world_statuses = {}

# Create the bot with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Predefined list of game slugs
predefined_games = ['dndextraordinaire-wd', 'dndextraordinaire-sh', 'dndextraordinaire-hws', 'dndextraordinaire-cos', 'dndextraordinaire-wc']

# Command: Whisper the list of predefined games to the user
@bot.command(name='list-games')
async def list_games(ctx):
    # Format the list of games as a string
    games_list = '\n'.join(predefined_games)
    
    # Try to send a direct message (DM) to the user
    try:
        await ctx.author.send(f"Here is a list of available games:\n{games_list}")
        await ctx.send(f"{ctx.author.mention}, I have sent you a DM with the list of available games.")
    except discord.Forbidden:
        # If the bot can't send a DM (e.g., user has DMs turned off), send a public message
        await ctx.send(f"{ctx.author.mention}, I couldn't send you a DM. Please check your privacy settings.")

# Load world statuses from file on bot startup
def load_world_statuses():
    global world_statuses
    try:
        with open('world_statuses.json', 'r') as f:
            world_statuses = json.load(f)
    except FileNotFoundError:
        world_statuses = {}

# Save world statuses to file after each update
def save_world_statuses():
    with open('world_statuses.json', 'w') as f:
        json.dump(world_statuses, f)

# Start a specific world by slug and update its status
def start_world(game_slug):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'content-type': 'application/json'
    }
    try:
        response = requests.post(f'https://forge-vtt.com/api/game/start', headers=headers, json={'game': game_slug})
        if response.status_code == 200:
            world_statuses[game_slug] = 'Online'  # Update world status
            print(f"Changing {game_slug}'s World status to Online")
            save_world_statuses()
            return True
        else:
            print(f"Error starting world: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

# Stop a specific world by slug and update its status
def stop_world(game_slug):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'content-type': 'application/json'
    }
    try:
        response = requests.post(f'https://forge-vtt.com/api/game/stop', headers=headers, json={'game': game_slug})
        if response.status_code == 200:
            world_statuses[game_slug] = 'Offline'  # Update world status
            print(f"Changing {game_slug}'s World status to Offline")
            save_world_statuses()
            return True
        else:
            print(f"Error stopping world: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

# Idle a specific world by slug and update its status
def idle_world(game_slug):
    headers = {
        'Access-Key': FORGE_API_KEY,
        'content-type': 'application/json'
    }
    try:
        response = requests.post(f'https://forge-vtt.com/api/game/idle', headers=headers, json={'game': game_slug})
        if response.status_code == 200:
            world_statuses[game_slug] = 'Idle'  # Update world status
            print(f"Changing {game_slug}'s World status to Idle")
            save_world_statuses()
            return True
        else:
            print(f"Error idling world: {response.text}")
            return False
    except Exception as e:
        print(f"Exception: {e}")
        return False

# Manually reset a world status (for edge case where bot wasn't online)
def reset_world_status(game_slug, status):
    world_statuses[game_slug] = status  # Manually set world status
    save_world_statuses()

# Load world statuses when the bot is ready
@bot.event
async def on_ready():
    load_world_statuses()
    print(f'Logged in as {bot.user.name}')
    print(f"Connected to: {', '.join([guild.name for guild in bot.guilds])}")

# Command: Start a world
@bot.command(name='world-on')
async def world_on(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if start_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now online.")
    else:
        await ctx.send("Failed to start the world. Please check the game slug or your permissions.")

# Command: Stop a world
@bot.command(name='world-off')
async def world_off(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if stop_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now offline.")
    else:
        await ctx.send("Failed to stop the world. Please check the game slug or your permissions.")

# Command: Idle a world
@bot.command(name='world-idle')
async def world_idle(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if idle_world(game_slug):
        await ctx.send(f"World '{game_slug}' is now idle.")
    else:
        await ctx.send("Failed to idle the world. Please check the game slug or your permissions.")

# Command: Check the status of all worlds
@bot.command(name='world-status')
async def world_status(ctx):
    if world_statuses:
        status_report = '\n'.join([f"World: {world}, Status: {status}" for world, status in world_statuses.items()])
        await ctx.send(f"World Status:\n{status_report}")
    else:
        await ctx.send("No world statuses available. You may need to start or stop a world first.")

# Command: Manually reset a world status (EDGE CASE handling)
@bot.command(name='reset-status')
async def reset_status(ctx, game_slug, status):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if status.lower() not in ['online', 'offline', 'idle']:
        await ctx.send("Invalid status. Valid statuses are 'online', 'offline', or 'idle'.")
        return

    reset_world_status(game_slug, status.capitalize())
    await ctx.send(f"World '{game_slug}' status has been manually reset to '{status.capitalize()}'.")

# Log any command errors
@bot.event
async def on_command_error(ctx, error):
    await ctx.send(f"An error occurred: {str(error)}")
    print(f"Error in command: {error}")

# Run the bot using the token from the .env file
bot.run(DISCORD_BOT_TOKEN)
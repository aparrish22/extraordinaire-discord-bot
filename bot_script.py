# Discord Bot for Managing ForgeVTT Worlds
# This bot allows trusted users to start, stop, idle, and check the status of game worlds on ForgeVTT.
# It uses Discord.py for bot interactions and Requests for API calls.
# Make sure to set up a .env file with DISCORD_BOT_TOKEN and FORGE_API_KEY.
# Required Libraries: discord.py, requests, python-dotenv
# To install dependencies, run:
# pip install discord.py requests python-dotenv
# Note: This script assumes you have a basic understanding of Python and Discord bot development
# and have already created a Discord bot and obtained its token.
# Author: Austin Parrish


import discord
from discord.ext import commands, tasks
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

# API URLS
FORGE_API_URL_WORLDS = 'https://forge-vtt.com/api/data/worlds'

# Define trusted users' Discord IDs
TRUSTED_USERS = [
    135630872652021761, # Dark
    89850959345246208, # Tanis
    279459304023654400, # Sarhara
    169688073226027008, # Stampapa
   # 254640527369175041 # ElPresidente
]  # Replace with actual trusted user IDs

# dictionary to track world statuses (online/offline)
# k = '
world_statuses = {}

# Create the bot with command prefix '!'
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Creating headers global variable for API requests
# contains access key and content type
headers = {
    'Access-Key': FORGE_API_KEY,
    'content-type': 'application/json'
}

# Predefined list of game slugs
predefined_games = ['dndextraordinaire-wd', 'dndextraordinaire-sh', 'dndextraordinaire-hws', 'dndextraordinaire-cos', 'dndextraordinaire-wc']

# TODO refer to Postman collection api tests
async def _get_status():
    # headers = {
    #     'Access-Key': FORGE_API_KEY,
    #     'content-type': 'application/json'
    # }
    try:
        response = requests.get(FORGE_API_URL_WORLDS, headers=headers)
        response.raise_for_status()
        status_data = response.json()
        new_status = status_data.get('status')  # Adjust based on actual response structure

        if new_status != current_status:
            # TODO
            print('')
            
    except Exception as e:
        print(f"Error fetching game status: {e}")

# auto check server status: bot's statuses VS server's statuses
@tasks.loop(minutes=360)
async def check_game_status():
    # headers = {
    #     'Access-Key': FORGE_API_KEY,
    #     'content-type': 'application/json'
    # }
    
    # TODO
    for w, s in world_statuses.items():
        if s.lower() != current_status:
            current_status = new_status

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
    # headers = {
    #     'Access-Key': FORGE_API_KEY,
    #     'content-type': 'application/json'
    # }
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
    # headers = {
    #     'Access-Key': FORGE_API_KEY,
    #     'content-type': 'application/json'
    # }
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
    # headers = {
    #     'Access-Key': FORGE_API_KEY,
    #     'content-type': 'application/json'
    # }
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
        await ctx.author.send(f"World '{game_slug}' is now online.")
    else:
        await ctx.send("Failed to start the world. Please check your game URL or your permissions.")

# Command: Stop a world
@bot.command(name='world-off')
async def world_off(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if stop_world(game_slug):
        await ctx.author.send(f"World '{game_slug}' is now offline.")
    else:
        await ctx.send("Failed to stop the world. Please check your game URL or your permissions.")

# Command: Idle a world
@bot.command(name='world-idle')
async def world_idle(ctx, game_slug):
    if ctx.author.id not in TRUSTED_USERS:
        await ctx.send("You do not have permission to use this command.")
        return

    if idle_world(game_slug):
        await ctx.author.send(f"World '{game_slug}' is now idle.")
    else:
        await ctx.send("Failed to idle the world. Please check your game URL or your permissions.")

# Command: Check the status of all worlds
@bot.command(name='world-status')
async def world_status(ctx):
    if world_statuses:
        cnt = 1
        status_report = ""
        
        for world, status in world_statuses.items():
            status_report += f"World {cnt}: {world} | Status: {status}\n"
            cnt += 1
        await ctx.author.send(f"World Status:\n{status_report}")
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
    await ctx.author.send(f"World '{game_slug}' status has been manually reset to '{status.capitalize()}'.")

# Log any command errors
@bot.event
async def on_command_error(ctx, error):
    await ctx.author.send(f"An error occurred: {str(error)}")
    print(f"Error in command: {error}")

# Run the bot using the token from the .env file
bot.run(DISCORD_BOT_TOKEN)
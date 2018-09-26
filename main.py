import discord
from discord.ext.commands import Bot
import sys
from discord.ext import commands
import configparser
import UserData
from collections import namedtuple
import asyncio
import datetime
import pickle
import random
import datetime_formatting

VERSION = "0.1"

# Reads the bot.ini file
parser = configparser.ConfigParser()
try:
    parser.read("bot.ini")
    prefix = parser.get("defaults", "prefix")
    token = parser.get("defaults", "token")
except configparser.NoSectionError:
    parser["defaults"] = {"prefix": "h!", "token": "<your token goes here>"}
    configfile = open("bot.ini", "w")
    parser.write(configfile)
    sys.exit("Please fill out the bot.ini file")

# Reads the data.pickle file
try:
    datafile = open("data.pickle", "rb")
    users, allowed_channels = pickle.load(datafile)
except (FileNotFoundError, EOFError) as e:
    users = {str: UserData.UserData}
    allowed_channels = {str: {str}}
    datafile = open("data.pickle", "wb")
    pickle.dump([users, allowed_channels], datafile)


def save():
    file = open("data.pickle", "wb")
    pickle.dump([users, allowed_channels], file)


# Initiates the bot
Client = discord.Client()
bot = commands.Bot(command_prefix=prefix)


@bot.event
async def on_ready():
    print("Bot is ready!")


# Commands available to everyone
@bot.command(name="sip", pass_context=True)  # Used by users to indicate they've drank and when to be reminded
async def sip(ctx, *time):
    discord.User.permissions_in()
    return


@bot.command(name="total", pass_context=True)  # Used by users to check how many times they've drank
async def total(ctx):
    return


@bot.command(name="stop", pass_context=True)  # Used by users to prevent the bot from sending them messages
async def stop(ctx):
    return


@bot.command(name="dmme", pass_context=True)  # Used by users to toggle whether they want the bot to send them dms
async def dmme(ctx):
    return


# Commands available only to moderators
@bot.command(name="allow_c", pass_context=True)  # Used by moderators to toggle this channel
async def allow_c(ctx):
    if ctx.message.author.server_permissons.manage_channels:
        g_id = ctx.message.guild.id
        c_id = ctx.message.channel.id
        if g_id in allowed_channels.keys():
            if allowed_channels.get(g_id).issuperset({c_id}):
                allowed_channels.get(g_id).remove(c_id)
                await bot.say("Removed %s from the list of allowed channels")
            else:
                allowed_channels.get(g_id).add(c_id)
        else:
            allowed_channels[g_id] = c_id
    else:
        return

bot.run(token)

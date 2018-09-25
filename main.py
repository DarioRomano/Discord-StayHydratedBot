import discord
from discord.ext.commands import Bot
import sys
from discord.ext import commands
import configparser
import asyncio
import datetime
import pickle
import random
import datetime_formatting

VERSION = "0.1"

parser = configparser.ConfigParser()
try:
    parser.read("bot.ini")
    prefix = parser.get("defaults", "prefix")
    token = parser.get("defaults", "token")
except configparser.NoSectionError:
    parser["defaults"] = {"prefix": "h!", "token": "<your token goes here>"}
    with open("bot.ini", "w") as configfile:
        parser.write(configfile)
    sys.exit("Please fill out the bot.ini file")


Client = discord.Client()
bot = commands.Bot(command_prefix=prefix)
allowed_channels = {"440720123448393728"}


@bot.event
async def on_ready():
    print("Bot is ready!")

bot.run(token)

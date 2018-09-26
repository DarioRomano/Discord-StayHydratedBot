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
    owner_id = int(parser.get("defaults", "owner_id"))
except configparser.NoSectionError:
    parser["defaults"] = {"prefix": "h!", "token": "<your token goes here>", "owner_id": "<your id goes here>"}
    configfile = open("bot.ini", "w")
    parser.write(configfile)
    sys.exit("Please fill out the bot.ini file")

# Reads the data.pickle file
try:
    datafile = open("data.pickle", "rb")
    users, allowed_channels = pickle.load(datafile)
except (FileNotFoundError, EOFError) as e:
    users = dict()
    allowed_channels = dict()
    datafile = open("data.pickle", "wb")
    pickle.dump([users, allowed_channels], datafile)


def save():
    file = open("data.pickle", "wb")
    pickle.dump([users, allowed_channels], file)


# Initiates the bot
Client = discord.Client()
bot = commands.Bot(command_prefix=prefix)


async def autosave():  # Background autosave
    while not bot.is_closed():
        save()
        await asyncio.sleep(5)


async def remind(user: int):
    user_data: UserData.UserData = users[user]
    if user_data.next_drink() < datetime.datetime.now():
        return
    time = user_data.next_drink() - datetime.datetime.now()
    await asyncio.sleep(time.seconds + time.days*24*60*60)
    if not (user_data.paused() or user_data.was_reminded()):
        await bot.get_channel(user_data.channel).send("Remember to stay hydrated <@%i>!" % user)
        user_data.remind()


@bot.event
async def on_ready():
    bot.loop.create_task(autosave())
    for user in users.keys():
        await remind(user)
    print("Bot is ready!")


# Commands available to everyone
@bot.command(name="sip", pass_context=True)  # Used by users to indicate they've drank and when to be reminded
async def sip(ctx: commands.Context, *time):
    dm = ctx.guild is None
    if not dm:
        if ctx.guild.id not in allowed_channels:
            return
        elif ctx.channel.id not in allowed_channels[ctx.guild.id]:
            return
    if ctx.author.id in users:
        user = users[ctx.author.id]
    else:
        if not dm:
            user = UserData.UserData(ctx.guild.id, ctx.channel.id)
        else:
            user = UserData.UserData(None, ctx.channel.id)
        users[ctx.author.id] = user
    if time.__len__() > 0:
        time = datetime_formatting.read_timedelta(list(time))
    else:
        time = user.drink_break

    if user.paused():
        await stop(ctx)

    if (dm and user.can_dm()) or not dm:
        if not dm:
            user.update_channel(ctx.guild.id, ctx.channel.id)
        else:
            user.update_channel(None, ctx.channel.id)
        user.set_break(time)
        user.drink()
        time = user.next_drink() - datetime.datetime.now()
        await ctx.send("Great! I will remind you to drink again in %s" % datetime_formatting.neat_timedelta(time))
    else:
        await ctx.send("You have not enabled direct messages. Enable them with ``%sdmme`` first" % prefix)
        return
    await remind(ctx.author.id)


@bot.command(name="total", pass_context=True)  # Used by users to check how many times they've drank
async def total(ctx: commands.Context):
    dm = ctx.guild is None
    if not dm:
        if ctx.guild.id not in allowed_channels:
            return
        if ctx.channel.id not in allowed_channels[ctx.guild.id]:
            return
    if ctx.author.id in users:
            user = users[ctx.author.id]
    else:
        if not dm:
            user = UserData.UserData(ctx.guild.id, ctx.channel.id)
        else:
            user = UserData.UserData(None, ctx.channel.id)
        users[ctx.author.id] = user

    if user.paused():
        await stop(ctx)

    if (dm and user.can_dm()) or not dm:
        await ctx.send("In total you've drank %i times" % user.times_drunk())
    else:
        await ctx.send("You have not enabled direct messages. Enable them with ``%sdmme`` first" % prefix)
        return


@bot.command(name="stop", pass_context=True)  # Used by users to prevent the bot from sending them messages
async def stop(ctx: commands.Context):
    dm = ctx.guild is None
    if not dm:
        if ctx.guild.id not in allowed_channels:
            return
        if ctx.channel.id not in allowed_channels[ctx.guild.id]:
            return
    if ctx.author.id in users:
        user = users[ctx.author.id]
    else:
        if not dm:
            user = UserData.UserData(ctx.guild.id, ctx.channel.id)
        else:
            user = UserData.UserData(None, ctx.channel.id)
        users[ctx.author.id] = user

    if (dm and user.can_dm()) or not dm:
        user.toggle_pause()
        if user.paused():
            await ctx.send("I will stop messaging you")
        else:
            await ctx.send("I will resume messaging you")


@bot.command(name="dmme", pass_context=True)  # Used by users to toggle whether they want the bot to send them dms
async def dmme(ctx: commands.Context):
    dm = ctx.guild is None
    if not dm:
        if ctx.guild.id not in allowed_channels:
            return
        if ctx.channel.id not in allowed_channels[ctx.guild.id]:
            return
    if ctx.author.id in users:
        user = users[ctx.author.id]
    else:
        if not dm:
            user = UserData.UserData(ctx.guild.id, ctx.channel.id)
        else:
            user = UserData.UserData(None, ctx.channel.id)
        users[ctx.author.id] = user

    if user.paused():
        await stop(ctx)

    user.toggle_dm()
    if user.can_dm():
        await ctx.send("I will now be able to send you direct messages")
    else:
        await ctx.send("I will no longer be able to send you direct messages")


# Commands available only to moderators
@bot.command(name="allow_c", pass_context=True)  # Used by moderators to toggle this channel
@commands.has_permissions(manage_channels=True)
async def allow_c(ctx: commands.Context):
    guild = ctx.guild.id
    channel = ctx.channel.id
    if guild in allowed_channels.keys():
        if channel in allowed_channels[guild]:
            allowed_channels.get(guild).remove(channel)
            await ctx.send("Removed <#%i> from the list of allowed channels" % channel)
        else:
            allowed_channels.get(guild).add(channel)
            await ctx.send("Added <#%i> to the list of allowed channels" % channel)
    else:
        allowed_channels[guild] = {channel}
        await ctx.send("Added <#%i> to the list of allowed channels" % channel)


# Commands available only to the bot owner
@bot.command(name="shutdown", pass_context=True)  # Used by the bot owner to safely shut down the bot
async def shutdown(ctx: commands.Context):
    if ctx.message.author.id == owner_id:
        save()
        await ctx.send("Saving data and shutting down...")
        await bot.logout()
    else:
        await ctx.send("This command can only be executed by the bot owner")
        return


bot.run(token)

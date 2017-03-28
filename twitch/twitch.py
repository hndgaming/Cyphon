from discord.ext import commands
from .utils.chat_formatting import *
import re
from .utils import checks
from .utils.dataIO import dataIO
from __main__ import send_cmd_help
import os
import asyncio
from copy import deepcopy
import aiohttp
import logging
import discord
import datetime
import traceback

class Twitch:
    def __init__(self, bot):
        self.bot = bot
        self.twitch_streams = dataIO.load_json("data/streams/twitch.json")
        self.settings = dataIO.load_json("data/streams/settings.json")
        self.permitted_role_admin = "Admin"

        self.stream_channel = "288915802135199754"  # live server
        self.dev_channel = "185833952278347793"  # live server
        self.server_id = "184694956131221515"  # live server
        self.check_delay = 60  # live delay

        # self.stream_channel = "295033190870024202"  # dev server
        # self.dev_channel = "288790607663726602"  # dev server
        # self.server_id = "215477025735966722"  # dev server
        # self.check_delay = 5  # debug delay


    @commands.group(name="twitch", pass_context=True)
    async def twitch(self, ctx):
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                if ctx.invoked_subcommand is None:
                    await send_cmd_help(ctx)
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="set_channel", pass_context=True)
    async def set_channel(self, ctx, channel):
        """Sets the streaming channel.
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                self.stream_channel = channel
                await self.bot.say("Channel sucessfully assigned.")
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="alert", pass_context=True)
    async def alert(self, ctx, stream: str):
        """Adds/removes twitch alerts from the current channel"""
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                stream = escape_mass_mentions(stream)
                regex = r'^(https?\:\/\/)?(www\.)?(twitch\.tv\/)'
                stream = re.sub(regex, '', stream)

                session = aiohttp.ClientSession()
                url = "https://api.twitch.tv/kraken/streams/" + stream
                header = {'Client-ID': self.settings.get("TWITCH_TOKEN", "")}
                try:
                    async with session.get(url, headers=header) as r:
                        data = await r.json()
                    await session.close()
                    if r.status == 400:
                        await self.bot.say("Owner: Client-ID is invalid or not set. "
                                           "See `{}streamset twitchtoken`"
                                           "".format(ctx.prefix))
                        return
                    elif r.status == 404:
                        await self.bot.say("That stream doesn't exist.")
                        return
                except:
                    await self.bot.say("Couldn't contact Twitch API. Try again later.")
                    return

                done = False

                for i, s in enumerate(self.twitch_streams):
                    if s["NAME"] == stream:
                        self.twitch_streams.remove(s)
                        await self.bot.say("Alert has been removed "
                                           "from the stream channel.")
                        done = True

                if not done:
                    self.twitch_streams.append(
                        {"CHANNEL": self.stream_channel, "IMAGE": None, "LOGO": None,
                         "NAME": stream, "STATUS": None, "ALREADY_ONLINE": False,
                         "GAME": None, "VIEWERS": None, "LANGUAGE": None,
                         "MESSAGE": None})
                    await self.bot.say("Alert activated. I will notify the stream channel "
                                       "everytime {} is live.".format(stream))

                dataIO.save_json("data/streams/twitch.json", self.twitch_streams)
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="stop", pass_context=True)
    async def stop_alert(self, ctx):
        """Stops all streams alerts in the stream channel"""
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                channel = ctx.message.channel

                to_delete = []

                for s in self.twitch_streams:
                    if channel.id in s["CHANNEL"]:
                        to_delete.append(s)

                for s in to_delete:
                    self.twitch_streams.remove(s)

                dataIO.save_json("data/streams/twitch.json", self.twitch_streams)

                await self.bot.say("There will be no more stream alerts in the stream "
                                   "channel.")
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="reset", pass_context=True)
    async def reset(self, ctx, user : str=None):
        """Resets all user settings.
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                for stream in self.twitch_streams:
                    if (user):
                        if (stream["NAME"] == user):
                            stream["MESSAGE"] = None
                            stream["ALREADY_ONLINE"] = False
                            stream["CHANNEL"] = self.stream_channel
                        else:
                            await self.bot.say("Stream does not exist")
                    else:
                        stream["MESSAGE"] = None
                        stream["ALREADY_ONLINE"] = False
                        stream["CHANNEL"] = self.stream_channel
                await self.bot.say("Reset complete.")
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="list", pass_context=True)
    async def list(self, ctx):
        """Lists all user entries.
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                message = []
                message.append("```\n")
                if self.check_channel(ctx):
                    if self.check_permission(ctx) or ctx.message.author == cyphon:
                        if len(self.twitch_streams) > 0:
                            for stream in self.twitch_streams:
                                message.append(stream["NAME"] + "\n")
                        else:
                            message.append("No streams found!")
                message.append("```")
                output = ''.join(message)
                await self.bot.say(output)
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    @twitch.command(name="info", pass_context=True)
    async def info(self, ctx, user : str=None):
        """Lists a user's details.
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        message = []
        message.append("```\n")

        if self.check_channel(ctx):
            if self.check_permission(ctx) or ctx.message.author == cyphon:
                if user:
                    for stream in self.twitch_streams:
                        if stream["NAME"] == user:
                            message.append("Stream name: " + str(stream["NAME"]) + "\n")

                            if stream["IMAGE"]:
                                message.append("Image URL: " + str(stream["IMAGE"]) + "\n")
                            else:
                                message.append("Image URL: N/A\n")

                            if stream["LOGO"]:
                                message.append("Logo URL: " + str(stream["LOGO"] + "\n"))
                            else:
                                message.append("Logo URL: N/A\n")

                            if stream["CHANNEL"]:
                                message.append("Assigned channel ID: " + str(stream["CHANNEL"]) + "\n")
                            else:
                                message.append("Assigned channel ID: N/A\n")

                            if stream["STATUS"]:
                                message.append("Status: " + str(stream["STATUS"]) + "\n")
                            else:
                                message.append("Status: N/A\n")

                            if stream["ALREADY_ONLINE"]:
                                message.append("ALREADY_ONLINE: " + str(stream["ALREADY_ONLINE"]) + "\n")
                            else:
                                message.append("ALREADY_ONLINE: N/A\n")

                            if stream["GAME"]:
                                message.append("Game: " + str(stream["GAME"]) + "\n")
                            else:
                                message.append("Game: N/A\n")

                            if stream["VIEWERS"]:
                                message.append("Viewers: " + str(stream["VIEWERS"]) + "\n")
                            else:
                                message.append("Viewers: N/A\n")

                            if stream["LANGUAGE"]:
                                message.append("Language: " + str(stream["LANGUAGE"]) + "\n")
                            else:
                                message.append("Language: N/A\n")

                            if stream["MESSAGE"]:
                                message.append("Message ID: " + str(stream["MESSAGE"]) + "\n")
                            else:
                                message.append("Message ID: N/A\n")

                            message.append("```\n")
                            output = ''.join(message)
                            await self.bot.say(output)

                else:
                    await self.bot.say("Please provide a user!")
            else:
                await self.bot.send_message(ctx.message.author, "You don't have permission to execute that command.")

    async def display_errors(self, stream):
        message = []
        message.append("```\n")

        message.append("Stream name: " + str(stream["NAME"]) + "\n")

        if stream["IMAGE"]:
            message.append("Image URL: " + str(stream["IMAGE"]) + "\n")
        else:
            message.append("Image URL: N/A\n")

        if stream["LOGO"]:
            message.append("Logo URL: " + str(stream["LOGO"] + "\n"))
        else:
            message.append("Logo URL: N/A\n")

        if stream["CHANNEL"]:
            message.append("Assigned channel ID: " + str(stream["CHANNEL"]) + "\n")
        else:
            message.append("Assigned channel ID: N/A\n")

        if stream["STATUS"]:
            message.append("Status: " + str(stream["STATUS"]) + "\n")
        else:
            message.append("Status: N/A\n")

        if stream["ALREADY_ONLINE"]:
            message.append("ALREADY_ONLINE: " + str(stream["ALREADY_ONLINE"]) + "\n")
        else:
            message.append("ALREADY_ONLINE: N/A\n")

        if stream["GAME"]:
            message.append("Game: " + str(stream["GAME"]) + "\n")
        else:
            message.append("Game: N/A\n")

        if stream["VIEWERS"]:
            message.append("Viewers: " + str(stream["VIEWERS"]) + "\n")
        else:
            message.append("Viewers: N/A\n")

        if stream["LANGUAGE"]:
            message.append("Language: " + str(stream["LANGUAGE"]) + "\n")
        else:
            message.append("Language: N/A\n")

        if stream["MESSAGE"]:
            message.append("Message ID: " + str(stream["MESSAGE"]) + "\n")
        else:
            message.append("Message ID: N/A\n")

        message.append("```\n")
        output = ''.join(message)

        cyphon = discord.utils.get(self.bot.get_server(self.server_id).members, id="186835826699665409")
        await self.bot.send_message(
            cyphon,
            output)

    def check_channel(self, ctx):
        if ctx.message.channel.id == self.dev_channel:
            return True

        return False

    def check_permission(self, ctx):
        server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
        admin = discord.utils.get(server_roles, name=self.permitted_role_admin)

        user_roles = ctx.message.author.roles

        if admin in user_roles:
            return True

        return False

    @twitch.command()
    @checks.is_owner()
    async def twitchtoken(self):
        """Sets the Client-ID for Twitch

        https://blog.twitch.tv/client-id-required-for-kraken-api-calls-afbb8e95f843"""
        self.settings["TWITCH_TOKEN"] = "6mmlypg9emj6jebbpylmlpejwxj2pn"
        dataIO.save_json("data/streams/settings.json", self.settings)
        await self.bot.say('Twitch Client-ID set.')
        
    async def twitch_online(self, stream):
        session = aiohttp.ClientSession()
        url = "https://api.twitch.tv/kraken/streams/" + stream["NAME"]
        header = {'Client-ID': self.settings.get("TWITCH_TOKEN", "")}
        try:
            async with session.get(url, headers=header) as r:
                data = await r.json()
            await session.close()
            if r.status == 400:
                return 400
            elif r.status == 404:
                return 404

            elif data["stream"] is None:
                stream["GAME"] = data["stream"]["game"]
                return False

            elif data["stream"]:
                if data["stream"]["game"]:
                    stream["GAME"] = data["stream"]["game"]
                else:
                    stream["GAME"] = "N/A"

                if data["stream"]["viewers"]:
                    stream["VIEWERS"] = data["stream"]["viewers"]
                else:
                    stream["VIEWERS"] = "0"

                if data["stream"]["channel"]["language"]:
                    stream["LANGUAGE"] = data["stream"]["channel"]["language"].upper()
                else:
                    stream["LANGUAGE"] = "N/A"

                if data["stream"]["preview"]["medium"]:
                    stream["IMAGE"] = data["stream"]["preview"]["medium"]
                else:
                    stream["IMAGE"] = None

                if data["stream"]["channel"]["logo"]:
                    stream["LOGO"] = data["stream"]["channel"]["logo"]
                else:
                    stream["LOGO"] = None

                if data["stream"]["channel"]["status"]:
                    stream["STATUS"] = data["stream"]["channel"]["status"]
                else:
                    stream["STATUS"] = "N/A"

                return True
        except Exception:
            cyphon = discord.utils.get(self.bot.get_server(self.server_id).members, id="186835826699665409")

            await self.bot.send_message(
                cyphon,
                traceback.format_exc())
            await self.display_errors(stream)
        return "error"

    async def stream_checker(self):
        CHECK_DELAY = self.check_delay
        counter = 0

        while self == self.bot.get_cog("Twitch"):

            print("ALIVE %s!" % counter)
            counter += 1

            old = deepcopy(self.twitch_streams)

            for stream in self.twitch_streams:
                online = await self.twitch_online(stream)

                if online is True and not stream["ALREADY_ONLINE"]:
                    try:
                        stream["ALREADY_ONLINE"] = True
                        channel_obj = self.bot.get_channel(stream["CHANNEL"])
                        if channel_obj is None:
                            continue
                        can_speak = channel_obj.permissions_for(channel_obj.server.me).send_messages
                        if channel_obj and can_speak:
                            data = discord.Embed(title=stream["STATUS"],
                                                 timestamp=datetime.datetime.now(),
                                                 colour=discord.Colour(value=int("05b207", 16)),
                                                 url="http://www.twitch.tv/%s" % stream["NAME"])
                            data.add_field(name="Streamer", value=stream["NAME"])
                            data.add_field(name="Status", value="Online")
                            data.add_field(name="Game", value=stream["GAME"])
                            data.add_field(name="Viewers", value=stream["VIEWERS"])
                            data.set_footer(text="Language: %s" % stream["LANGUAGE"])
                            if (stream["IMAGE"]):
                                data.set_image(url=stream["IMAGE"])
                            if (stream["LOGO"]):
                                data.set_thumbnail(url=stream["LOGO"])

                            # if stream["CHANNEL"] and stream["MESSAGE"]:
                            #     channel = self.bot.get_channel(stream["CHANNEL"])
                            #
                            #     message = await self.bot.get_message(channel, stream["MESSAGE"])
                            #
                            #     await self.bot.edit_message(message, embed=data)
                            # else:
                            await self.bot.send_message(
                                self.bot.get_channel(stream["CHANNEL"]),
                                embed=data)
                            async for message in self.bot.logs_from(self.bot.get_channel(stream["CHANNEL"]), limit=1):
                                stream["MESSAGE"] = message.id
                    except Exception:
                        cyphon = discord.utils.get(self.bot.get_server(self.server_id).members, id="186835826699665409")

                        await self.bot.send_message(
                            cyphon,
                            traceback.format_exc())
                        await self.display_errors(stream)

                elif online is True and stream["ALREADY_ONLINE"]:
                    try:
                        data = discord.Embed(title=stream["STATUS"],
                                             timestamp=datetime.datetime.now(),
                                             colour=discord.Colour(value=int("05b207",16)),
                                             url="http://www.twitch.tv/%s" % stream["NAME"])
                        data.add_field(name="Streamer", value=stream["NAME"])
                        data.add_field(name="Status", value="Online")
                        data.add_field(name="Game", value=stream["GAME"])
                        data.add_field(name="Viewers", value=stream["VIEWERS"])
                        data.set_footer(text="Language: %s" % stream["LANGUAGE"])
                        if (stream["IMAGE"]):
                            data.set_image(url=stream["IMAGE"])
                        if (stream["LOGO"]):
                            data.set_thumbnail(url=stream["LOGO"])

                        channel = self.bot.get_channel(stream["CHANNEL"])
                        message = await self.bot.get_message(channel, stream["MESSAGE"])

                        await self.bot.edit_message(message, embed=data)
                    except Exception:
                        cyphon = discord.utils.get(self.bot.get_server(self.server_id).members, id="186835826699665409")

                        await self.bot.send_message(
                            cyphon,
                            traceback.format_exc())
                        await self.display_errors(stream)

                else:
                    if stream["ALREADY_ONLINE"] and not online:
                        stream["ALREADY_ONLINE"] = False
                        try:
                            # data = discord.Embed(title=stream["STATUS"],
                            #                      timestamp=datetime.datetime.now(),
                            #                      colour=discord.Colour(value=int("990303", 16)),
                            #                      url="http://www.twitch.tv/%s" % stream["NAME"])
                            # data.add_field(name="Status", value="Offline")
                            # data.set_footer(text="Language: %s" % stream["LANGUAGE"])
                            # if (stream["LOGO"]):
                            #     data.set_thumbnail(url=stream["LOGO"])
                            #
                            channel = self.bot.get_channel(stream["CHANNEL"])
                            message = await self.bot.get_message(channel, stream["MESSAGE"])

                            stream["MESSAGE"] = None

                            await self.bot.delete_message(message)
                        except Exception:
                            cyphon = discord.utils.get(self.bot.get_server(self.server_id).members,
                                                       id="186835826699665409")

                            await self.bot.send_message(
                                cyphon,
                                traceback.format_exc())
                            await self.display_errors(stream)

                await asyncio.sleep(0.5)

            if old != self.twitch_streams:
                dataIO.save_json("data/streams/twitch.json", self.twitch_streams)

            await asyncio.sleep(CHECK_DELAY)

    # @commands.group(name="deb", pass_context=True)
    # async def deb(self, ctx):
    #     if ctx.invoked_subcommand is None:
    #         await send_cmd_help(ctx)
    #
    # @deb.command(name="test", pass_context=True)
    # async def test(self, ctx):
    #     for stream in self.twitch_streams:
    #         await self.bot.say("Stream: %s" % stream["NAME"])
    #         await self.bot.say("Channel: %s" % self.bot.get_channel(stream["CHANNEL"]))
    #         await self.bot.say("Status: " + str(stream["ALREADY_ONLINE"]))
    #         await self.bot.say("Game: " + stream["GAME"])
    #         await self.bot.say("Viewers: " + str(stream["VIEWERS"]))
    #
    # @deb.command(name="toggle", pass_context=True)
    # async def toggle(self, ctx):
    #     for stream in self.twitch_streams:
    #         stream["ALREADY_ONLINE"] = False
    #         if stream["MESSAGE"] and stream["CHANNEL"]:
    #             try:
    #                 channel = self.bot.get_channel(stream["CHANNEL"])
    #                 print(str(stream["MESSAGE"]))
    #                 message = await self.bot.get_message(channel, stream["MESSAGE"])
    #                 print("d3")
    #                 print(str(message))
    #                 await self.bot.delete_message(message)
    #                 print("d4")
    #             except Exception as e:
    #                 print("Exception: " + str(e))
    #
    #
    # @deb.command(name="say", pass_context=True)
    # async def say(self, ctx):
    #     await self.bot.say("%s" % ctx.message.content)

def check_folders():
    if not os.path.exists("data/streams"):
        print("Creating data/streams folder...")
        os.makedirs("data/streams")


def check_files():
    f = "data/streams/twitch.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty twitch.json...")
        dataIO.save_json(f, [])

    f = "data/streams/settings.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty settings.json...")
        dataIO.save_json(f, {})



def setup(bot):
    logger = logging.getLogger('aiohttp.client')
    logger.setLevel(50)  # Stops warning spam
    check_folders()
    check_files()
    n = Twitch(bot)
    loop = asyncio.get_event_loop()
    loop.create_task(n.stream_checker())
    bot.add_cog(n)

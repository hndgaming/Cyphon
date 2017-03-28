import datetime
from discord.ext import commands
import discord
from .utils.dataIO import dataIO
import os
import asyncio
class LFG:
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = 45
        self.cooldown_json = dataIO.load_json("data/lfg/cooldown.json")
        self.broadcasting = True
        self.permitted_channel = "288795776459603968"  # live server
        # self.permitted_channel = "288681028284055552"  # dev server
        self.permitted_role_admin = "Admin"  # live server
        # self.permitted_role_admin = "LFGPermission"  # dev server
        self.permitted_role_staff = "Staff"  # live server

    # async def poll(self, user):
    #     session = aiohttp.ClientSession()
    #     url = "http://localhost:4444/api/v3/u/" + user + "/blob"
    #     header = {'User-Agent': "Mozilla/5.0 (Windows NT 6.1)"}
    #     async with session.get(url, headers=header) as r:
    #         data = await r.json()
    #     await session.close()
    #     if r.status == 400:
    #         return 400
    #     elif r.status == 404:
    #         return 404
    #     return data

    @commands.group(pass_context=True, no_pm=True)
    async def lfg(self, ctx):
        if self.check_channel(ctx):
            if ctx.invoked_subcommand is None:
                await self.bot.say("Hi! Please read the pinned message at the start of this thread or use ``.lfg help`` for further instructions.")

    @lfg.command(name="help", pass_context=True)
    async def help(self, ctx):
        """Sends bot instructions to the user.
        """
        if self.check_channel(ctx):
            await self.bot.delete_message(ctx.message)
            msg = "Welcome to the LFG bot! The commands are used as follows:\n\n" \
                "∙ `.lfg sub <mode> <region>` subscribes you to the specified LFG-role. *E.g:* `lfg sub cp eu`\n" \
                "∙ `.lfg unsub <mode> <region>` unsubscribes you from the specified LFG-role. *E.g:* `.lfg unsub qp na`\n" \
                "∙ `.lfg search <mode> <region> <text>` can be used to search for other players with the specified LFG-role. Don't forget to add your text here! *E.g:* `.lfg search cp eu Anyone in the 2500 - 3000 range want to group up?`\n\n" \
                "Options for `<mode>` are `cp` or `qp`. Options for `<region>` are `eu` or `na`."
            try:
                await self.bot.send_message(ctx.message.author, msg)
            except discord.errors.Forbidden:
                await self.bot.say("We couldn't send you the instructions, %s! Check if you allowed DMs and then try again!" % ctx.message.author.mention)

    @lfg.command(name="sub", pass_context=True)
    async def subscribe(self, ctx, mode: str = None, region: str = None):
        """Subscribes users to LFG.
            Usage:  .lfg sub <mode> <region>
            e.g.    .lfg sub qp na
                    .lfg sub cp eu
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                await self.bot.delete_message(ctx.message)
                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                CasualNA = discord.utils.get(server_roles, name="LFGCasualNA")
                competitiveNA = discord.utils.get(server_roles, name="LFGCompetitiveNA")
                CasualEU = discord.utils.get(server_roles, name="LFGCasualEU")
                competitiveEU = discord.utils.get(server_roles, name="LFGCompetitiveEU")

                user_roles = ctx.message.author.roles

                if mode:
                    mode = mode.lower()
                if region:
                    region = region.lower()

                if mode == "qp" and region == "na":
                    role = CasualNA
                elif mode == "cp" and region == "na":
                    role = competitiveNA
                elif mode == "qp" and region == "eu":
                    role = CasualEU
                elif mode == "cp" and region == "eu":
                    role = competitiveEU


                try:
                    if role in user_roles:
                        try:
                            await self.bot.send_message(ctx.message.author, "You already have the role %s." % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s, you already have the role %s." % (ctx.message.author.mention, role))
                    else:
                        await self.bot.add_roles(ctx.message.author, role)
                        if self.broadcasting:
                            await self.bot.say("%s just subscribed to %s!" % (ctx.message.author.mention, role))
                        else:
                            try:
                                await self.bot.send_message(ctx.message.author, "You successfully subscribed to %s." % role)
                            except discord.errors.Forbidden:
                                await self.bot.say("%s just subscribed to %s!" % (ctx.message.author.mention, role))
                except UnboundLocalError:
                    try:
                        await self.bot.send_message(ctx.message.author, "Please specify a correct mode and region!\nYour input was: ``%s``.\nUse ``.lfg help``for more information!" % ctx.message.content)
                    except discord.errors.Forbidden:
                        await self.bot.say("%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lfg help`` for more information!" % (ctx.message.author.mention, ctx.message.content))
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lfg.command(name="unsub", pass_context=True)
    async def unsubscribe(self, ctx, mode: str = None, region: str = None):
        """Unsubscribes users from LFG.
             Usage:  .lfg unsub <mode> <region>
             e.g.    .lfg unsub qp na
                     .lfg unsub cp eu
         """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                await self.bot.delete_message(ctx.message)
                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                CasualNA = discord.utils.get(server_roles, name="LFGCasualNA")
                competitiveNA = discord.utils.get(server_roles, name="LFGCompetitiveNA")
                CasualEU = discord.utils.get(server_roles, name="LFGCasualEU")
                competitiveEU = discord.utils.get(server_roles, name="LFGCompetitiveEU")

                user_roles = ctx.message.author.roles

                if mode:
                    mode = mode.lower()
                if region:
                    region = region.lower()

                if mode == "qp" and region == "na":
                    role = CasualNA
                elif mode == "cp" and region == "na":
                    role = competitiveNA
                elif mode == "qp" and region == "eu":
                    role = CasualEU
                elif mode == "cp" and region == "eu":
                    role = competitiveEU

                try:
                    if role in user_roles:
                        await self.bot.remove_roles(ctx.message.author, role)
                        try:
                            await self.bot.send_message(ctx.message.author, "You successfully unsubscribed from %s." % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s successfully unsubscribed from &s." % (ctx.message.author.mention, role))
                    else:
                        try:
                            await self.bot.send_message(ctx.message.author, "You don't have the role %s!" % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s, you don't have the role %s!" % (ctx.message.author.mention, role))
                except UnboundLocalError:
                    # if removeAll:
                    #     roles = [CasualNA, competitiveNA, CasualEU, competitiveEU]
                    #
                    #     for r in roles:
                    #         if r in user_roles:
                    #             time.sleep(1)
                    #             await self.bot.remove_roles(ctx.message.author, r)
                    #
                    #     await self.bot.say("All LFG roles have been removed from %s!" % (ctx.message.author.mention))
                    # else:
                    try:
                        await self.bot.send_message(ctx.message.author, "Please specify a correct mode and region!\nYour input was: ``%s``.\nUse ``.lfg help``for more information!" % ctx.message.content)
                    except discord.errors.Forbidden:
                        await self.bot.say(
                            "%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lfg help`` for more information!" % (
                            ctx.message.author.mention, ctx.message.content))
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lfg.command(name="search", pass_context=True)
    async def search(self, ctx, mode: str = None, region: str = None):
        """Lets users search via LFG.
            Usage:  .lfg search <mode> <region>
            e.g.    .lfg search qp na
                    .lfg search cp eu
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                message = ctx.message.content[18:]
                await self.bot.delete_message(ctx.message)

                if mode:
                    mode = mode.lower()
                if region:
                    region = region.lower()

                if mode == 'qp':
                    localMode = mode
                elif mode == 'cp':
                    localMode = mode

                if region == 'na':
                    localRegion = region
                if region == 'eu':
                    localRegion = region

                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                casualNA = discord.utils.get(server_roles, name="LFGCasualNA")
                competitiveNA = discord.utils.get(server_roles, name="LFGCompetitiveNA")
                casualEU = discord.utils.get(server_roles, name="LFGCasualEU")
                competitiveEU = discord.utils.get(server_roles, name="LFGCompetitiveEU")

                cooldown = self.check_cooldown(ctx)
                if not cooldown:
                    try:
                        if localMode == 'qp' and localRegion == 'na':
                            await self.bot.edit_role(ctx.message.server, casualNA, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, casualNA.mention, message))
                            await self.bot.edit_role(ctx.message.server, casualNA, mentionable=False)
                        elif localMode == 'cp' and localRegion == 'na':
                            await self.bot.edit_role(ctx.message.server, competitiveNA, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, competitiveNA.mention, message))
                            await self.bot.edit_role(ctx.message.server, competitiveNA, mentionable=False)
                        elif localMode == 'qp' and localRegion == 'eu':
                            await self.bot.edit_role(ctx.message.server, casualEU, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, casualEU.mention, message))
                            await self.bot.edit_role(ctx.message.server, casualEU, mentionable=False)
                        elif localMode == 'cp' and localRegion == 'eu':
                            await self.bot.edit_role(ctx.message.server, competitiveEU, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, competitiveEU.mention, message))
                            await self.bot.edit_role(ctx.message.server, competitiveEU, mentionable=False)
                    except UnboundLocalError:
                        try:
                            await self.bot.send_message(ctx.message.author, "Please specify a correct mode and region!\nYour input was: ``%s.``\nUse ``.lfg help``for more information!" % ctx.message.content)
                        except discord.errors.Forbidden:
                            await self.bot.say(
                                "%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lfg help`` for more information!" % (
                                ctx.message.author.mention, ctx.message.content))
                        del (self.cooldown_json[ctx.message.author.id])
                        dataIO.save_json('data/lfg/cooldown.json', self.cooldown_json)
                else:
                    try:
                        await self.bot.send_message(ctx.message.author, cooldown)
                    except discord.errors.Forbidden:
                        await self.bot.say(cooldown)
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lfg.command(name="reset", pass_context=True)
    async def reset(self, ctx):
        """Resets a users' cooldown.
            Usage:  .lfg reset <user>
        """
        if self.check_channel(ctx, "dev"):
            if self.check_permission(ctx, "both"):
                try:
                    del (self.cooldown_json[ctx.message.mentions[0].id])
                    dataIO.save_json('data/lfg/cooldown.json', self.cooldown_json)
                    await self.bot.say("Cooldown reset for %s" % ctx.message.mentions[0].mention)
                except KeyError:
                    await self.bot.say("User %s does not have a cooldown" % ctx.message.mentions[0])
            else:
                await self.bot.say("You don't have permission to execute that command.")

    @lfg.command(name="broadcast", pass_context=True)
    async def broadcast(self, ctx):
        """Toggles broadcasting on or off.
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx, "dev"):
            if self.check_permission(ctx, "admin") or ctx.message.author == cyphon:
                self.broadcasting = not self.broadcasting

                if self.broadcasting:
                    await self.bot.say("Broadcasting subscribers is now turned on!")
                else:
                    await self.bot.say("Broadcasting subscribers is now turned off!")
            else:
                await self.bot.say("You don't have permission to execute that command.")

    @lfg.command(name="cleanup", pass_context=True)
    async def cleanup(self, ctx, arg: str = None):
        """Clears the lfg-channel.
            Optional parameter 'all' clears even bot messages.
            Usage:  .lfg cleanup [all]
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")

        if self.check_channel(ctx, "dev"):
            if self.check_permission(ctx, "admin") or ctx.message.author == cyphon:
                to_delete = []

                if arg:
                    arg.lower()

                channels = [channel for channel in ctx.message.server.channels]
                channel = self.bot.get_channel(self.permitted_channel)

                async for message in self.bot.logs_from(channel):
                    if arg is None:
                        if message.author.id != self.bot.user.id:
                            to_delete.append(message)
                    elif arg == "all":
                        to_delete.append(message)

                await self.mass_purge(to_delete)

                if arg == "all":
                    await self.bot.send_message(channel, "Welcome to the HND LFG system! Our bot is designed to enable players to find people to play with, without the drawback of constant mentions!\n\n" \
                            "To get started, subscribe to one of the four roles you want to get notifications for by using:\n" \
                            "``.lfg sub <mode> <region>``\n\n" \
                           "The options for ``<mode>`` are ``cp`` for competitive and ``qp`` for casual (quickplay + arcade).\n" \
                           "The options for ``<region>`` are ``eu`` and ``na``.\n\n" \
                           "Now, if someone is looking for other players to play Overwatch with, you will receive a notification if you subscribed to their combination of mode and region! Try it yourself by using:\n" \
                           "``.lfg search <mode> <region> <text>``\n\n" \
                           "Be aware: This command has a cooldown period of 45 minutes so don't forget to add additional descriptive text!\n\n" \
                           "We also offer the same module for team-finding! Just use the commands:\n" \
                           "``.lft sub <region>`` and\n" \
                           "``.lft search <region> <text>``\n" \
                           "for this purpose!\n\n" \
                            "To unsubscribe from a role, you can use:\n" \
                            "``.lfg unsub <mode> <region>`` or ``.lft unsub <region>`` respectively.")
            else:
                await self.bot.say("You don't have permission to execute that command.")

    async def mass_purge(self, messages):
        while messages:
            if len(messages) > 1:
                await self.bot.delete_messages(messages[:100])
                messages = messages[100:]
            else:
                await self.bot.delete_message(messages[0])
                messages = []
            await asyncio.sleep(1.5)

    def check_channel(self, ctx, choice: str = None):
        channels = [channel for channel in ctx.message.server.channels]
        channel = self.bot.get_channel(self.permitted_channel)

        if choice is None:
            if ctx.message.channel == channel:
                return True
        elif choice is "dev":
            channel = discord.utils.get(channels, name="dev")
            if ctx.message.channel == channel:
                return True

        return False

    def check_permission(self, ctx, choice: str = None):
        server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
        admin = discord.utils.get(server_roles, name=self.permitted_role_admin)
        staff = discord.utils.get(server_roles, name=self.permitted_role_staff)

        user_roles = ctx.message.author.roles

        if choice == "admin":
            if admin in user_roles:
                return True
        elif choice == "both":
            if admin in user_roles or staff in user_roles:
                return True

        return False

    def check_cooldown(self, ctx):
        user = ctx.message.author
        currenttime = datetime.datetime.now()
        try:
            if currenttime < datetime.datetime.strptime(self.cooldown_json[user.id]['cooldown'], '%Y-%m-%d %H:%M:%S.%f'):
                timecalc = datetime.datetime.strptime(self.cooldown_json[user.id]['cooldown'], '%Y-%m-%d %H:%M:%S.%f') - currenttime
                time = datetime.datetime.strptime(str(timecalc), '%H:%M:%S.%f')
                msg = "You can't use LFG right now. Try again in " + str(
                    datetime.datetime.strftime(time, '%H:%M:%S'))
                return msg
            elif currenttime >= datetime.datetime.strptime(self.cooldown_json[user.id]['cooldown'], '%Y-%m-%d %H:%M:%S.%f'):
                del (self.cooldown_json[user.id])
                dataIO.save_json('data/lfg/cooldown.json', self.cooldown_json)
                return None
        except KeyError:
            self.cooldown_json[user.id] = {}
            local_cd = currenttime + datetime.timedelta(minutes=self.cooldown)
            self.cooldown_json[user.id]['cooldown'] = str(local_cd)
            dataIO.save_json('data/lfg/cooldown.json', self.cooldown_json)
            return None


def check_folders():
    if not os.path.exists("data/lfg"):
        print("Creating data/lfg folder...")
        os.makedirs("data/lfg")


def check_files():
    f = "data/lfg/cooldown.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty cooldown.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    n = LFG(bot)
    bot.add_cog(n)
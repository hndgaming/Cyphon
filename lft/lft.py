import datetime
from discord.ext import commands
import discord
from .utils.dataIO import dataIO
import os

class LFT:
    def __init__(self, bot):
        self.bot = bot
        self.cooldown = 1440
        self.cooldown_json = dataIO.load_json("data/lft/cooldown.json")
        self.broadcasting = True
        self.permitted_channel = "288795776459603968"  # live server
        # self.permitted_channel = "288681028284055552"  # dev server
        self.permitted_role_admin = "Admin"  # live server
        # self.permitted_role_admin = "LFGPermission"  # dev server
        self.permitted_role_staff = "Staff"  # live server

    @commands.group(pass_context=True, no_pm=True)
    async def lft(self, ctx):
        if self.check_channel(ctx):
            if ctx.invoked_subcommand is None:
                await self.bot.say("Hi! Please read the pinned message at the start of this thread or use ``.lft help`` for further instructions.")

    @lft.command(name="help", pass_context=True)
    async def help(self, ctx):
        """Sends bot instructions to the user.
        """
        if self.check_channel(ctx):
            await self.bot.delete_message(ctx.message)
            msg = "Welcome to the LFT bot! The commands are used as follows:\n\n" \
                "∙ `.lft sub <region>` subscribes you to the specified LFT-role. *E.g:* `lft sub eu`\n" \
                "∙ `.lft unsub <region>` unsubscribes you from the specified LFT-role. *E.g:* `.lft unsub na`\n" \
                "∙ `.lft search <region> <text>` can be used to search for other players with the specified LFT-role. Don't forget to add your text here! *E.g:* `.lft search eu Looking for a Reinhardt player, SR 3000+`\n\n" \
                "Options for `<region>` are `eu` or `na`."
            try:
                await self.bot.send_message(ctx.message.author, msg)
            except discord.errors.Forbidden:
                await self.bot.say(
                    "We couldn't send you the instructions, %s! Check if you allowed DMs and then try again!" % ctx.message.author.mention)

    @lft.command(name="sub", pass_context=True)
    async def subscribe(self, ctx, region: str = None):
        """Subscribes users to LFT.
            Usage:  .lft sub <region>
            e.g.    .lft sub NA
                    .lft sub EU
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                await self.bot.delete_message(ctx.message)
                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                LFT_NA = discord.utils.get(server_roles, name="LFT_NA")
                LFT_EU = discord.utils.get(server_roles, name="LFT_EU")

                user_roles = ctx.message.author.roles

                if region:
                    region = region.lower()

                if region == 'na':
                    role = LFT_NA
                elif region == 'eu':
                    role = LFT_EU

                try:
                    if role in user_roles:
                        try:
                            await self.bot.send_message(ctx.message.author, "You already have the role %s!" % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s, you already have the role %s!" % (ctx.message.author.mention, role))
                    else:
                        await self.bot.add_roles(ctx.message.author, role)
                        if self.broadcast:
                            await self.bot.say("%s just subscribed to %s!" % (ctx.message.author.mention, role))
                        else:
                            try:
                                await self.bot.send_message(ctx.message.author, "You successfully subscribed to %s." % role)
                            except discord.errors.Forbidden:
                                await self.bot.say("%s just subscribed to %s!" % (ctx.message.author.mention, role))
                except UnboundLocalError:
                    try:
                        await self.bot.send_message(ctx.message.author,"Please specify a correct mode and region!\nYour input was: ``%s``.\nUse ``.lft help``for more information!" % ctx.message.content)
                    except discord.errors.Forbidden:
                        await self.bot.say(
                            "%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lft help`` for more information!" % (
                            ctx.message.author.mention, ctx.message.content))
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lft.command(name="unsub", pass_context=True)
    async def unsubscribe(self, ctx, region: str = None):
        """Unsubscribes users from LFT.
             Usage:  .lft unsub <region>
             e.g.    .lft unsub NA
                     .lft unsub EU
         """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                await self.bot.delete_message(ctx.message)
                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                LFT_NA = discord.utils.get(server_roles, name="LFT_NA")
                LFT_EU = discord.utils.get(server_roles, name="LFT_EU")

                user_roles = ctx.message.author.roles

                if region:
                    region = region.lower()

                if region == "na":
                    role = LFT_NA
                elif region == "eu":
                    role = LFT_EU
                # elif region == "all":
                #     removeAll = True

                try:
                    if role in user_roles:
                        await self.bot.remove_roles(ctx.message.author, role)
                        try:
                            await self.bot.send_message(ctx.message.author, "You successfully unsubscribed from %s." % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s successfully unsubscribed from %s." % (ctx.message.author.mention, role))
                    else:
                        try:
                            await self.bot.send_message(ctx.message.author, "You don't have the role %s!" % role)
                        except discord.errors.Forbidden:
                            await self.bot.say("%s, you don't have the role %s!" % (ctx.message.author.mention, role))
                except UnboundLocalError:
                    # if removeAll:
                    #     roles = [LFT_NA, LFT_EU]
                    #
                    #     async for r in roles:
                    #         if r in user_roles:
                    #             await self.bot.remove_roles(ctx.message.author, r)
                    #
                    #     await self.bot.send_message(ctx.message.author, "All LFT roles have been removed from you!")
                    # else:
                    try:
                        await self.bot.send_message(ctx.message.author,"Please specify a correct mode and region!\nYour input was: ``%s``.\nUse ``.lft help``for more information!" % ctx.message.content)
                    except discord.errors.Forbidden:
                        await self.bot.say(
                            "%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lft help`` for more information!" % (
                            ctx.message.author.mention, ctx.message.content))
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lft.command(name="search", pass_context=True)
    async def search(self, ctx, region: str = None):
        """Lets users search via LFT.
            Usage:  .lft search <region>
            e.g.    .lft search na
                    .lft search eu
        """
        cyphon = discord.utils.get(ctx.message.server.members, id="186835826699665409")
        try:
            if self.check_channel(ctx):
                message = ctx.message.content[15:]
                await self.bot.delete_message(ctx.message)

                if region:
                    region = region.lower()

                if region == 'na':
                    localRegion = region
                if region == 'eu':
                    localRegion = region

                server_roles = [role for role in ctx.message.server.roles if not role.is_everyone]
                LFT_NA = discord.utils.get(server_roles, name="LFT_NA")
                LFT_EU = discord.utils.get(server_roles, name="LFT_EU")

                cooldown = self.check_cooldown(ctx)
                if not cooldown:
                    try:
                        if localRegion == 'na':
                            await self.bot.edit_role(ctx.message.server, LFT_NA, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, LFT_NA.mention, message))
                            await self.bot.edit_role(ctx.message.server, LFT_NA, mentionable=False)
                        elif localRegion == 'eu':
                            await self.bot.edit_role(ctx.message.server, LFT_EU, mentionable=True)
                            await self.bot.say("User %s is %s:\n%s" % (ctx.message.author.mention, LFT_EU.mention, message))
                            await self.bot.edit_role(ctx.message.server, LFT_EU, mentionable=False)
                    except UnboundLocalError:
                        try:
                            await self.bot.send_message(ctx.message.author,"Please specify a correct mode and region!\nYour input was: ``%s``.\nUse ``.lft help``for more information!" % ctx.message.content)
                        except discord.errors.Forbidden:
                            await self.bot.say(
                                "%s, please specify a correct mode and region!\nYour input was: ``%s``.\n Use ``.lft help`` for more information!" % (
                                    ctx.message.author.mention, ctx.message.content))
                        del (self.cooldown_json[ctx.message.author.id])
                        dataIO.save_json('data/lft/cooldown.json', self.cooldown_json)
                else:
                    try:
                        await self.bot.send_message(ctx.message.author, cooldown)
                    except discord.errors.Forbidden:
                        await self.bot.say(cooldown)
        except Exception as e:
            await self.bot.send_message(cyphon, "User: %s\nReported error: %s\nMessage: %s" % (ctx.message.author, e, ctx.message.content))
            await self.bot.say("Your request caused an error! A report has been forwarded to the developer.")

    @lft.command(name="reset", pass_context=True)
    async def reset(self, ctx):
        """Resets a users' cooldown.
             Usage:  .lft reset <user>
         """
        if self.check_channel(ctx, "dev"):
            if self.check_permission(ctx, "both"):
                try:
                    del (self.cooldown_json[ctx.message.mentions[0].id])
                    dataIO.save_json('data/lft/cooldown.json', self.cooldown_json)
                    await self.bot.say("Cooldown reset for %s" % ctx.message.mentions[0].mention)
                except KeyError:
                    await self.bot.say("User %s does not have a cooldown" % ctx.message.mentions[0])
            else:
                await self.bot.say("You don't have permission to execute that command.")

    @lft.command(name="broadcast", pass_context=True)
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
                msg = "You can't use LFT right now. Try again in " + str(
                    datetime.datetime.strftime(time, '%H:%M:%S'))
                return msg
            elif currenttime >= datetime.datetime.strptime(self.cooldown_json[user.id]['cooldown'], '%Y-%m-%d %H:%M:%S.%f'):
                del (self.cooldown_json[user.id])
                dataIO.save_json('data/lft/cooldown.json', self.cooldown_json)
                return None
        except KeyError:
            self.cooldown_json[user.id] = {}
            local_cd = currenttime + datetime.timedelta(minutes=self.cooldown)
            self.cooldown_json[user.id]['cooldown'] = str(local_cd)
            dataIO.save_json('data/lft/cooldown.json', self.cooldown_json)
            return None


def check_folders():
    if not os.path.exists("data/lft"):
        print("Creating data/lft folder...")
        os.makedirs("data/lft")


def check_files():
    f = "data/lft/cooldown.json"
    if not dataIO.is_valid_json(f):
        print("Creating empty cooldown.json...")
        dataIO.save_json(f, {})


def setup(bot):
    check_folders()
    check_files()
    n = LFT(bot)
    bot.add_cog(n)

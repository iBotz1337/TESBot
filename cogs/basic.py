import discord, os, random, requests, async_cse, asyncio, io
from datetime import datetime
from discord.ext import commands, menus
from pymongo import MongoClient

class SnipeMenu(menus.Menu):
    def __init__(self, ctx, csn):
        super().__init__()
        self.ctx = ctx
        self.csn = csn
        self.pg = 0
    
    def genEmbed(self):
        embed = discord.Embed()
        embed.set_author(name="Snipe Menu", icon_url=self.ctx.me.avatar_url)
        embed.description = f"Last {len(self.csn)} deleted messages in {self.ctx.channel.mention}."
        return embed
                    
    def getPagewiseDetails(self, pg):
        msg = self.csn[pg]
        embed = self.genEmbed()
        embed.clear_fields()
        links = []
        if msg.attachments:
            for att in msg.attachments:
                links.append(att.proxy_url)
        val = f"**From** {self.ctx.bot.emotes.get('arrowright','')} {msg.author.mention}\n**Message** {self.ctx.bot.emotes.get('arrowright','')} {self.ctx.bot.emotes.get('message','')}\n{msg.content}\n\n"
        embed.add_field(name="\u200b", value=val)
        if links:
            links = [f"[attachment-{i+1}]({links[i]})" for i in range(len(links))]
            val = f"{', '.join(links)}"
            embed.add_field(name="\u200b", value=f"**Attachment(s)** {self.ctx.bot.emotes.get('arrowright','')}\n {val}", inline=False)
        embed.set_footer(text = f"{self.ctx.author.name} | Snipe Menu | Page {self.pg + 1} of {len(self.csn)}", icon_url = self.ctx.author.avatar_url)
        return embed
                    
    def check(self, payload):
        return payload.message_id == self.message.id and payload.user_id == self.ctx.author.id
                    
    async def send_initial_message(self, ctx, channel):
        embed = self.getPagewiseDetails(self.pg)
        return await channel.send(embed=embed)
    
    buttonz = {"first": "<:first:800209150227120158>","back": "<:back:800215055634399232>", "stop": "<:stop:800214101791735808>", "next": "<:next:800214875669528596>", "last": "<:last:800209919734972426>"}
    
    @menus.button(buttonz.get("first"))
    async def on_first_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = 0
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    
    @menus.button(buttonz.get("back"))
    async def on_previous_button(self, payload):
        if not self.check(payload):
            return
        self.pg -= 1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
                
    @menus.button(buttonz.get("stop"))
    async def on_stop_button(self, payload):
        if not self.check(payload):
            return
        self.stop()
        await self.message.delete()
                        
    @menus.button(buttonz.get("next"))
    async def on_next_button(self, payload):
        if not self.check(payload):
            return 
        self.pg += 1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
        
    @menus.button(buttonz.get("last"))
    async def on_last_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = -1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))

class ESnipeMenu(menus.Menu):
    def __init__(self, ctx, csn):
        super().__init__()
        self.ctx = ctx
        self.csn = csn
        self.pg = 0
    
    def genEmbed(self):
        embed = discord.Embed()
        embed.set_author(name="Esnipe Menu", icon_url=self.ctx.me.avatar_url)
        embed.description = f"Last {len(self.csn)} edited messages in {self.ctx.bot.emotes.get('textchannel','')}{self.ctx.channel.name}."
        return embed
                    
    def getPagewiseDetails(self, pg):
        msg = self.csn[pg]
        embed = self.genEmbed()
        embed.clear_fields()
        bf, af = msg["before"], msg["after"]
        val1 = f"{bf.author.mention} {self.ctx.bot.emotes.get('arrowright','')}\n {bf.content}" 
        val2 = f"{af.author.mention} {self.ctx.bot.emotes.get('arrowright','')}\n {af.content}"
        embed.add_field(name=f"{self.ctx.bot.emotes.get('message','')} Original Message", value=val1)
        embed.add_field(name=f"{self.ctx.bot.emotes.get('message','')} Edited Message", value=val2)
        embed.set_footer(text = f"{self.ctx.author.name} | Esnipe Menu | Page {self.pg + 1} of {len(self.csn)}", icon_url = self.ctx.author.avatar_url)
        return embed
                    
    def check(self, payload):
        return payload.message_id == self.message.id and payload.user_id == self.ctx.author.id
                    
    async def send_initial_message(self, ctx, channel):
        embed = self.getPagewiseDetails(self.pg)
        return await channel.send(embed=embed)
    
    buttonz = {"first": "<:first:800209150227120158>","back": "<:back:800215055634399232>", "stop": "<:stop:800214101791735808>", "next": "<:next:800214875669528596>", "last": "<:last:800209919734972426>"}
    
    @menus.button(buttonz.get("first"))
    async def on_first_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = 0
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    
    @menus.button(buttonz.get("back"))
    async def on_previous_button(self, payload):
        if not self.check(payload):
            return
        self.pg -= 1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
                
    @menus.button(buttonz.get("stop"))
    async def on_stop_button(self, payload):
        if not self.check(payload):
            return
        self.stop()
        await self.message.delete()
                        
    @menus.button(buttonz.get("next"))
    async def on_next_button(self, payload):
        if not self.check(payload):
            return 
        self.pg += 1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
        
    @menus.button(buttonz.get("last"))
    async def on_last_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = -1
        self.pg %=  len(self.csn)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    

class GoogleMenu(menus.Menu):
    def __init__(self, ctx, query, results):
        super().__init__()
        self.ctx = ctx
        self.query = query
        self.results = results
        self.pg = 0
    
    def genEmbed(self):
        embed = discord.Embed()
        embed.set_author(name="Google Search", icon_url= "https://i.imgur.com/uTmJl1x.png")
        embed.title = f"Search results for: {self.query}"
        embed.set_footer(text="Google", icon_url= "https://i.imgur.com/uTmJl1x.png")
        return embed
    
    def getPagewiseDetails(self, pg):
        result = self.results[pg]
        embed = self.genEmbed()
        embed.description = f"**[{result.title}]({result.url})**\n{result.description}\n{result.url}\n\n"
        embed.set_footer(text=f"Google | Page {pg+1} of {len(self.results)}", icon_url= "https://i.imgur.com/uTmJl1x.png")
        img_url = result.image_url
        if img_url.endswith(("jpg", "jpeg", "png", "gif")):
            if not img_url.endswith("google.jpg"):
                embed.set_image(url=img_url)
            else:
                embed.set_image(url="")
        else:
            embed.set_image(url="")
        return embed
                    
    def check(self, payload):
        return payload.message_id == self.message.id and payload.user_id == self.ctx.author.id
                    
    async def send_initial_message(self, ctx, channel):
        embed = self.getPagewiseDetails(self.pg)
        return await channel.send(embed=embed)
    
    buttonz = {"first": "<:first:800209150227120158>","back": "<:back:800215055634399232>", "stop": "<:stop:800214101791735808>", "next": "<:next:800214875669528596>", "last": "<:last:800209919734972426>"}
    
    @menus.button(buttonz.get("first"))
    async def on_first_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = 0
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    
    @menus.button(buttonz.get("back"))
    async def on_previous_button(self, payload):
        if not self.check(payload):
            return
        self.pg -= 1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
                
    @menus.button(buttonz.get("stop"))
    async def on_stop_button(self, payload):
        if not self.check(payload):
            return
        self.stop()
        await self.message.delete()
                        
    @menus.button(buttonz.get("next"))
    async def on_next_button(self, payload):
        if not self.check(payload):
            return 
        self.pg += 1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
        
    @menus.button(buttonz.get("last"))
    async def on_last_button(self, payload):
        if not self.check(payload):
            return 
        self.pg = -1
        self.pg %=  len(self.results)
        await self.message.edit(embed=self.getPagewiseDetails(self.pg))
    

class Basic(commands.Cog):

    def __init__(self, client):
        self.client = client

    try:
        mclient = MongoClient(os.environ.get('mongodb'))
        db = mclient.get_database("my_db")
    except:
        print('Cannot connect to MongoDB at the moment!')

    # <# Event: On Guild Join - Start #>

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        prefixes = self.db.get_collection("prefixes")
        p = prefixes.find_one({"serverid": guild.id})
        if not p:
            prefixes.insert_one({"serverid": guild.id, "prefix": "!"})

    # <# Event: On Guild Join - End #>

    # <# Event: On Guild Remove - Start #>

    @commands.Cog.listener()
    async def on_guild_remove(self, guild):
        prefixes = self.db.get_collection("prefixes")
        p = prefixes.find_one({"serverid": guild.id})
        if p:
            prefixes.delete_one({"serverid": guild.id})

    # <# Event: On Guild Remove - End #>


    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        if before.content != after.content:
            if not before.guild:
                return
            if before.author.bot:
                return 
            channel = before.channel
            guild = before.guild
            guildEditedMsgs = self.client.esnipes.get(guild.id, {})
            channelEditedMsgs = guildEditedMsgs.get(channel.id, [])
            
            if len(channelEditedMsgs) >= 9:
                channelEditedMsgs = channelEditedMsgs[-9:]
            channelEditedMsgs.append({"before" : before, "after" : after})
            guildEditedMsgs[channel.id] = channelEditedMsgs
            self.client.esnipes[guild.id] = guildEditedMsgs
    
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        if not message.guild:
            return
        if message.author.bot:
            return
        channel = message.channel
        guild = message.guild
        guildDeletedMsgs = self.client.snipes.get(guild.id, {})
        channelDeletedMsgs = guildDeletedMsgs.get(channel.id, [])
        
        if len(channelDeletedMsgs) >= 9:
            channelDeletedMsgs = channelDeletedMsgs[-9:]
        channelDeletedMsgs.append(message)
        guildDeletedMsgs[channel.id] = channelDeletedMsgs
        self.client.snipes[guild.id] = guildDeletedMsgs

    @commands.command(aliases = ["change_prefix", "cp", "changeprefix"])
    @commands.guild_only()
    @commands.check_any(commands.has_permissions(manage_guild = True), commands.is_owner())
    async def prefix(self, ctx, *, new_prefix):
        """Changes command prefix."""
        new_prefix = new_prefix.replace('"','').replace("'","")
        if 0 < len(new_prefix) <= 10:
            def check(message):
                return message.author == ctx.author and any(
                    i == message.content.lower() for i in ["y", "n", "yes", "no", "confirm"])
    
            m = f"Hello {ctx.author.display_name}, \nCommand prefix will be changed to {self.client.emotes.get('arrowright','**')} {new_prefix} {self.client.emotes.get('arrowleft','**')}\nPlease confirm if you want to continue? \nType any of these `[y/yes/confirm]`"
            embed = discord.Embed(description = m)
            x = await ctx.send(embed = embed)
            try:
                msg = await self.client.wait_for("message", timeout = 20.0, check = check)
            except asyncio.TimeoutError:
                embed = discord.Embed(description = f"{self.client.emotes.get('timer','')} Session timed out! Command prefix did not change.",
                                      color = discord.Color.red())
                await x.edit(embed = embed)
            else:
                if any(i == msg.content.lower() for i in ["y", "yes", "confirm"]):
                    prefixes = self.db.get_collection("prefixes")
                    p = prefixes.find_one({"serverid": ctx.guild.id})
                    prefixes.update_one({"serverid": ctx.guild.id}, {"$set": {"prefix": new_prefix}})
                    desc = f"{self.client.emotes.get('accepted','')} Command prefix changed to {self.client.emotes.get('arrowright','**')} {new_prefix} {self.client.emotes.get('arrowleft','**')}"
                    embed = discord.Embed(title = f"Hello {ctx.author.display_name}",
                                  description = desc)
                    await x.edit(embed = embed)
                else:
                    desc = f"{self.client.emotes.get('denied','')} Command prefix did not change."
                    embed = discord.Embed(title = f"Hello {ctx.author.display_name}",
                                  description = desc)
                    await x.edit(embed = embed)
    
        else:
            embed = discord.Embed(description = f"{self.client.emotes.get('alert','')} Command prefixes can only be of 1 to 10 characters long.",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command()
    async def ping(self, ctx):
        """Displays Bot latency."""
        await ctx.send(f"{self.client.emotes.get('typing','')} `Pong! {round(self.client.latency * 1000, 2)}ms.`")

    @commands.command(aliases = ["info", "botinfo", "bi", "bot_info"])
    async def bot(self, ctx):
        """Displays Bot information."""
        owner = self.client.get_user(self.client.ownerid)
        desc = f"{self.client.emotes.get('arrowright','')} I'm a multi-purpose bot made by {self.client.emotes.get('owner','')} **{owner}** for Pokemon Creed and some day to day Discord uses.\n\nCheck out `help` command to know more about me!"
        if self.client.inviteurl:
            desc += f"\n\n[Click here to join the Bot Testing Server!]({self.client.inviteurl})\n"
        embed = discord.Embed(description = desc, color = discord.Color.dark_teal())
        embed.set_author(name = f"{ctx.me}", icon_url = ctx.me.avatar_url)
        embed.set_thumbnail(url = ctx.me.avatar_url)
        embed.add_field(name = f"{self.client.emotes.get('developer','')} Developer:", value = f"{owner.mention}", inline=True)
        embed.add_field(name = f"{self.client.emotes.get('bot','')} Bot ID:", value = f"`{self.client.user.id}`", inline=True)
        embed.add_field(name = f"{self.client.emotes.get('typing','')} Latency:", value = f"{self.client.emotes.get('arrowright','')}  {round(self.client.latency * 1000, 2)}ms", inline=True)
        embed.add_field(name = f"{self.client.emotes.get('discord','')} Servers:", value = f"{self.client.emotes.get('arrowright','')}  {len(self.client.guilds)}", inline=True)
        embed.add_field(name = f"{self.client.emotes.get('user','')} Members:", value = f"{self.client.emotes.get('arrowright','')}  {len(self.client.users)}", inline=True)
        embed.add_field(name = f"{self.client.emotes.get('maintenance','')} Version:", value = f"{self.client.emotes.get('arrowright','')}  `2.0.0`", inline=True)
        embed.set_footer(text = f"{owner}   •   {self.client.get_time}", icon_url=owner.avatar_url)
        await ctx.send(embed = embed)

    @commands.command(aliases = ["serverinfo", "si", "server_info"])
    @commands.guild_only()
    async def server(self, ctx):
        """Displays server details."""
        mem_count = len([m for m in ctx.guild.members if not m.bot])
        bot_count = len([m for m in ctx.guild.members if m.bot])
        roles = ", ".join([r.mention for r in ctx.guild.roles][::-1])
        embed = discord.Embed(description = "**Roles:**\n" + roles,
                              color = discord.Color.dark_teal())
        embed.set_author(name = f"{ctx.guild.name}")
        embed.set_thumbnail(url = ctx.guild.icon_url)
        embed.set_image(url = ctx.guild.banner_url)
        embed.add_field(name = f"{self.client.emotes.get('owner','')} Owner:", value = f"{ctx.guild.owner.mention}", inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Members Count:", value = f"{self.client.emotes.get('user','')} **Users:** {mem_count}\n{self.client.emotes.get('bot','')} **Bots:** {bot_count}",
                        inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Channels Count:",
                        value = f"{self.client.emotes.get('textchannel','')} **Text Channels:** {len(ctx.guild.text_channels)}\n{self.client.emotes.get('voicechannel','')} **Voice Channels:** {len(ctx.guild.voice_channels)}\n{self.client.emotes.get('category','')} **Categories:** {len(ctx.guild.categories)}",
                        inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Nitro Boosts:", value = f"{self.client.emotes.get('boost','')} {str(ctx.guild.premium_subscription_count)}", inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Created on:",
                        value = f"{str(ctx.guild.created_at.date())} ({(datetime.now() - ctx.guild.created_at).days} days ago)",
                        inline = False)
        await ctx.send(embed = embed)

    @commands.group(aliases = ["sn"])
    @commands.guild_only()
    async def snipe(self, ctx):
        """Snipes deleted message."""
        if ctx.invoked_subcommand is None:
            gsn = self.client.snipes.get(ctx.guild.id, {})
            if gsn:
                csn = gsn.get(ctx.channel.id, [])
                if csn:
                    msg = csn[-1]
                    links = []
                    if msg.attachments:
                        for att in msg.attachments:
                            links.append(att.proxy_url)
                    embed = discord.Embed(description = f"{self.client.emotes.get('textchannel','')} **Channel:** {msg.channel.mention}\n{self.client.emotes.get('message','')} **Message:**\n{msg.content}")
                    embed.set_author(name = msg.author.name, icon_url = msg.author.avatar_url)
                    embed.set_footer(text = f"Snipe Request: {ctx.author.name}", icon_url = ctx.author.avatar_url)
                    if links:
                        embed.set_image(url = links[0])
        
                    await ctx.send(embed = embed)
                else:
                    await ctx.send("`There\'s nothing to snipe here!`")
            else:
                await ctx.send("`There\'s nothing to snipe here!`")
    
    @snipe.command(name = "menu")
    @commands.guild_only()
    async def snipe_menu(self, ctx):
        """Shows last 10 deleted messages"""
        gsn = self.client.snipes.get(ctx.guild.id, {})
        if gsn:
            csn = gsn.get(ctx.channel.id, [])[::-1]
            if csn:
                sm = SnipeMenu(ctx, csn)
                await sm.start(ctx)
            else:
                await ctx.send("`No snipes in this channel!`")
        else:
            await ctx.send("`No snipes in this channel!`")

                            
    @commands.group(aliases = ["esn"])
    @commands.guild_only()
    async def esnipe(self, ctx):
        """Snipes edited message."""
        if ctx.invoked_subcommand is None:
            gsn = self.client.esnipes.get(ctx.guild.id, {})
            if gsn:
                csn = gsn.get(ctx.channel.id, [])
                if csn:
                    msg = csn[-1]
                    bf, af = msg["before"], msg["after"]
                    embed = discord.Embed(description = f"{self.client.emotes.get('textchannel','')} **Channel:** {ctx.channel.mention}\n\n{self.client.emotes.get('message','')} **Original Message:**\n{bf.content}\n\n{self.client.emotes.get('message','')} **Edited Message:**\n{af.content}\n\n{self.client.emotes.get('arrowright','')} [Jump to the message]({bf.jump_url})")
                    embed.set_author(name = bf.author.name, icon_url = bf.author.avatar_url)
                    embed.set_footer(text = f"Esnipe Request: {ctx.author.name}", icon_url = ctx.author.avatar_url)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("`There\'s nothing to snipe here!`")
            else:
                await ctx.send("`There\'s nothing to snipe here!`")
    
    @esnipe.command(name = "menu")
    @commands.guild_only()
    async def esnipe_menu(self, ctx):
        """Shows last 10 edited messages"""
        gsn = self.client.esnipes.get(ctx.guild.id, {})
        if gsn:
            csn = gsn.get(ctx.channel.id, [])
            if csn:
                esm = ESnipeMenu(ctx, csn)
                await esm.start(ctx)
            else:
                await ctx.send("`No snipes in this channel!`")
        else:
            await ctx.send("`No snipes in this channel!`")
    
    @commands.command(aliases = ["toss"])
    async def flip(self, ctx):
        """Flips a coin."""
        result = random.choice(["Heads", "Tails"])
        await ctx.send(f"You flipped a coin and it\'s {result}!")

    @commands.command(aliases = ["who"])
    @commands.guild_only()
    async def whois(self, ctx, *, member: discord.Member = None):
        """Displays user details."""
        if not member:
            member = ctx.author
        desc = "**Server Permissions:**\n"
        has_perm = ""
        has_not_perm = ""
        imp_perms = ["Create Instant Invite", "Kick Members", "Ban Members", "Administrator", "Manage Channels",
                     "Manage Guild", "View Audit Log", "Read Messages", "Send Messages", "Manage Messages",
                     "Embed Links", "Attach Files", "Read Message History", "Mention Everyone", "Manage Nicknames",
                     "Manage Roles", "Manage Emojis"]
        for perm in member.guild_permissions:
            if perm[0].replace("_", " ").title() in imp_perms:
                if perm[1] is True:
                    has_perm += perm[0].replace("_", " ").title() + ", "
                else:
                    has_not_perm += perm[0].replace("_", " ").title() + ", "
        if has_perm:
            desc += f"{self.client.emotes.get('greentick', '')} `" + has_perm[:-2] + "`\n\n"
        if has_not_perm:
            desc += f"{self.client.emotes.get('redtick', '')} `" + has_not_perm[:-2] + "`\n\n"

        roles = ", ".join([r.mention for r in member.roles][::-1])
        desc += f"{self.client.emotes.get('arrowright','')} **Server Roles:**\n" + roles

        embed = discord.Embed(description = desc,
                              color = discord.Color.teal())
        embed.set_author(name = member.name, icon_url = member.avatar_url)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Status: ", value = f"{self.client.emotes.get(str(member.status),'')} " + str(member.status).title(), inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Activity: ", value = str(member.activity).title(), inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Joined Discord: ",
                        value = f"{self.client.emotes.get('in','')} {member.created_at.date()} ({(datetime.now() - member.created_at).days} Days ago)",
                        inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Joined {ctx.guild.name}: ",
                        value = f"{self.client.emotes.get('in', '')} {member.joined_at.date()} ({(datetime.now() - member.joined_at).days} Days ago)",
                        inline = False)
        embed.add_field(name = f"{self.client.emotes.get('arrowright','')} Nickname: ", value = member.nick, inline = False)
        embed.set_thumbnail(url = member.avatar_url)
        await ctx.send(embed = embed)

    @commands.command(aliases = ["av", "pfp"])
    async def avatar(self, ctx, *, member: discord.Member = None):
        """Displays user avatar."""
        if not member:
            member = ctx.author
        ext = "gif" if member.is_avatar_animated() else "png"
        file = discord.File(io.BytesIO(await member.avatar_url.read()), f"{ctx.author.id}.{ext}")
        embed = discord.Embed()
        embed.set_image(url= f"attachment://{ctx.author.id}.{ext}")
        await ctx.send(file=file, embed=embed)

    @commands.command(aliases = ["calc", "cal", "="])
    async def calculate(self, ctx, *, expression = ""):
        """Calculates the expression and displays the result."""
        if expression:
            _expression = expression.replace(" ", "").replace("^", "**").replace(",","")
            try:
                result = eval(_expression)
            except:
                result = "invalid"
            if result != "invalid":
                msg = f"{self.client.emotes.get('greentick','')} `{expression} = {result:,}`"
            else:
                msg = f"{self.client.emotes.get('redtick','')} `Cannot evaluate this expression: {expression}`"
            await ctx.send(msg)
        else:
            msg = f"{self.client.emotes.get('redtick','')}  `Invalid expression to evaluate.`"
            await ctx.send(msg)

    @commands.command(name = "random", aliases = ["rand", "roll"])
    async def _random(self, ctx, *, args = "0 100"):
        """Generates a random number. (accepts space seperated interval)"""
        try:
            args = sorted(list(map(int, args.split())))
        except Exception as e:
            raise e
        if len(args) == 2:
            start, end = args[0], args[1]
        elif len(args) == 1:
            start, end = 0, args[0]
        else:
            raise ValueError
        if start == end:
            result = start
        else:
            result = random.randrange(start, end)
        await ctx.send(result)

    @commands.command(aliases = ["pick"])
    async def choose(self, ctx, *, args):
        """Selects a random option from the (comma seperated) given options."""
        try:
            args = list(map(str.strip, args.split(",")))
        except Exception as e:
            raise e
        result = random.choice(args)
        await ctx.send(f"{result}")

    @commands.command(hidden = True, aliases = [])
    async def meme(self, ctx, *, category= None):
        """Displays a random meme from reddit."""
        if ctx.guild.id != 997006222853144627:
            return

        try:
            memeAPI = "https://meme-api.herokuapp.com/gimme"
            if category:
                category = category.replace(" ","")
                memeAPI += "/" + category
            response = requests.get(memeAPI)
            m = response.json()
            embed = discord.Embed()
            embed.description = m["title"] + f"\n\n**Source:** [Click here]({m['postLink']})"
            embed.set_image(url=m["url"])
            footer_text = f"Author: {m['author']} | Upvotes: {m['ups']} | Category: {m['subreddit']}"
            embed.set_footer(text=footer_text)
            await ctx.send(embed = embed)
        except:
            embed = discord.Embed(title = "#404 - Not Found")
            embed.description = "I couldn't find a meme at the moment."
            await ctx.send(embed = embed)

    @commands.command(aliases = ["gs"])
    @commands.cooldown(1, 15, commands.BucketType.user)
    async def google(self, ctx, *, query = None):
        """Googles your query and displays results."""
        if query is None:
            embed = discord.Embed()
            embed.set_author(name="Google Search", icon_url= "https://i.imgur.com/uTmJl1x.png")
            embed.set_image(url = "https://i.imgur.com/gS9R4pa.gif")
            embed.description = "Google Search command is used to search various functionalities of google and display the search results."
            embed.set_footer(text="To search Google | google [query here]", icon_url= "https://i.imgur.com/uTmJl1x.png")
            await ctx.send(embed=embed)
            return
        else:
            try:
                gclient = async_cse.Search(os.environ.get("googleapikey").split(","))
                results = await gclient.search(query, safesearch=False)
                await gclient.close()
            except:
                results = []
                await gclient.close()
            
            if results:
                m = GoogleMenu(ctx, query, results)
                await m.start(ctx)
            else:
                embed = discord.Embed()
                embed.set_author(name="Google Search", icon_url= "https://i.imgur.com/uTmJl1x.png")
                embed.title = f"Search results for: {query}"
                #embed.set_footer(text="Google", icon_url= "https://i.imgur.com/uTmJl1x.png")
                embed.description = "`No results found!`"
                await ctx.send(embed=embed)
    
    @commands.command()
    async def poll(self, ctx, *, details = ""):
        """Creates a Poll with the given details."""
        if details:
            embed = discord.Embed()
            embed.description = details
            embed.set_author(name=f"Poll by: {ctx.author}", icon_url= ctx.author.avatar_url)
            embed.set_footer(text=f"Created on: {self.client.get_time}", icon_url=ctx.me.avatar_url)
            reac = [self.client.emotes.get("upvote",""), self.client.emotes.get("downvote")]
            try:
                await ctx.message.delete()
            except:
                pass
            pollmessage = await ctx.send(embed=embed)
            for r in reac:
                await pollmessage.add_reaction(r)
        else:
            await ctx.send("Poll cannot be created with blank description!")
                
    # <# Basic Error Handler - Start #>

    @prefix.error
    @whois.error
    @avatar.error
    @_random.error
    @choose.error
    @meme.error
    @google.error
    @calculate.error
    @poll.error
    async def basic_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description = f"`Hi {ctx.author.name}, Please provide required arguments for {ctx.command.name} command!`",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description = f"`Hi {ctx.author.name}, You are on cooldown. Please retry after {round(error.retry_after)}s.`",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(description = f"`Hi {ctx.author.name}, {str(error)}`",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description = f"`Hi {ctx.author.name}, I do not have the following permissions: {error.missing_perms}`",
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = f"`{str(error)}`", color = discord.Color.red())
            await ctx.send(embed = embed)

    # <# Basic Error Handler - End #>

def setup(client):
    client.add_cog(Basic(client))
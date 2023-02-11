import discord, sqlite3, json, re, os, asyncio, aiohttp
from discord.ext import commands
from imgurpython import ImgurClient
from pymongo import MongoClient

class Owner(commands.Cog):
    """Exclusive commands for EliteBOY"""
    def __init__(self, client):
        self.client = client

    try:
        mclient = MongoClient(os.environ.get("mongodb"))
        db = mclient.get_database("my_db")
    except:
        print("Cannot connect to MongoDB at the moment!")

    @commands.command(hidden = True, aliases = ['imgur'])
    @commands.is_owner()
    async def imgurupload(self, ctx, *, upURL = None):
        """Uploads the image to imgur.com"""
        try:
            links = []
            if upURL:
                links.extend(re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*(),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+\.(?:jpg|jpeg|gif|png)', upURL))
            if ctx.message.attachments or links:
                embed = discord.Embed()
                embed.title = f"{self.client.emotes.get('loading','')} Imgur - Upload"
                embed.description = f"```Upload in progress...\nThis might take some time...\nLinks will be available here soon!```"
                embed.set_footer(text = f'Requested By: {ctx.author.name}', icon_url = ctx.author.avatar)
                embed.set_thumbnail(url = 'https://i.imgur.com/kotofyF.png')
                x = await ctx.send(embed = embed)
                await ctx.message.delete()
                for att in ctx.message.attachments:
                    links.append(att.proxy_url)
                if links:
                    uploadedURLs = []
                    iclient_id, iclient_secret = os.environ.get('imgur').split(':')
                    iclient = ImgurClient(iclient_id, iclient_secret)
                    for link in links:
                        upload = iclient.upload_from_url(link)
                        uploadedURLs.append(upload['link'])
                    desc = f"" + '\n'.join(uploadedURLs)
                    embed.title = f"{self.client.emotes.get('greentick','')} Image(s) uploaded to imgur.com"
                    embed.description = "```" + desc + "```"
                    embed.set_footer(text = f'Upload Count: {len(uploadedURLs)} | Requested By: {ctx.author.name}', icon_url = ctx.author.avatar)
                    embed.set_thumbnail(url = 'https://i.imgur.com/kotofyF.png')
                    await x.edit(embed = embed)

            else:
                await ctx.send('`Please add atleast one image as an attachment [or provide valid image link(s)] to upload to imgur.`')
        except Exception as e:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `upload failed: {str(e)}`")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def load(self, ctx, extension):
        """Loads the given extension."""
        try:
            await self.client.load_extension(f'cogs.{extension}')
            await ctx.send(f"{self.client.emotes.get('greentick','')} `Hi {ctx.author.name}, Successfully loaded [{extension}] extension.`")
        except commands.ExtensionAlreadyLoaded:
            await ctx.send(f"{self.client.emotes.get('alert','')} `Hi {ctx.author.name}, [{extension}] extension is already loaded.`")
        except commands.ExtensionNotFound:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Hi {ctx.author.name}, [{extension}] extension not found.`")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def unload(self, ctx, extension):
        """Unloads the given extension."""
        if extension.lower() == 'owner':
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Hi {ctx.author.name}, [{extension}] extension cannot be unloaded! You can use reload command.`")
            return
        try:
            await self.client.unload_extension(f'cogs.{extension}')
            await ctx.send(f"{self.client.emotes.get('greentick','')} `Hi {ctx.author.name}, Successfully unloaded [{extension}] extension.`")
        except commands.ExtensionNotLoaded:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Hi {ctx.author.name}, Cannot unload an extension which is not loaded at all.`")
        except commands.ExtensionNotFound:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Hi {ctx.author.name}, [{extension}] extension not found.`")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def reload(self, ctx, extension):
        """Reloads the given extension."""
        try:
            await self.client.unload_extension(f'cogs.{extension}')
            await self.client.load_extension(f'cogs.{extension}')
            await ctx.send(f"{self.client.emotes.get('greentick','')} `Hi {ctx.author.name}, Successfully reloaded [{extension}] extension.`")
        except commands.ExtensionNotLoaded:
            try:
                await self.client.load_extension(f'cogs.{extension}')
                await ctx.send(f"{self.client.emotes.get('greentick','')} `Hi {ctx.author.name}, Successfully reloaded [{extension}] extension.`")
            except commands.ExtensionNotFound:
                await ctx.send(f"{self.client.emotes.get('redtick','')} `Hi {ctx.author.name}, [{extension}] extension not found.`")

    @commands.command(hidden = True)
    @commands.is_owner()
    async def disable(self, ctx, cmd_name):
        """Disables the given command."""
        if cmd_name:
            cmd = self.client.get_command(cmd_name)
        else:
            embed = discord.Embed(description = f'Hello {ctx.author.name}, Please provide a valid command to `disable`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
            return

        if cmd:
            if cmd.enabled:
                cmd.enabled = False
                embed = discord.Embed(description = f'Hello {ctx.author.name},\nCommand: `{cmd.name}` has been `disabled` successfully.',
                                      color = discord.Color.teal())
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(description = f'Hello {ctx.author.name},\nCommand: `{cmd.name}` is already `disabled`.',
                                      color = discord.Color.red())
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = f'Hello {ctx.author.name}, Command: `{cmd.name}` Not Found.',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def enable(self, ctx, cmd_name):
        """Enables the given command."""
        if cmd_name:
            cmd = self.client.get_command(cmd_name.lower())
        else:
            embed = discord.Embed(description = f'Hello {ctx.author.name}, Please provide a valid command to `enable`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
            return

        if cmd:
            if not cmd.enabled:
                cmd.enabled = True
                embed = discord.Embed(description = f'Hello {ctx.author.name},\nCommand: `{cmd.name}` has been `enabled` successfully.',
                                      color = discord.Color.teal())
                await ctx.send(embed = embed)
            else:
                embed = discord.Embed(description = f'Hello {ctx.author.name},\nCommand: `{cmd.name}` is already `enabled`.',
                                      color = discord.Color.red())
                await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = f'Hello {ctx.author.name}, Command: `{cmd.name}` Not Found!',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command(hidden = True)
    @commands.is_owner()
    async def sql(self, ctx, *, query):
        """Run SQL Query with `bot.db`."""
        botdb = sqlite3.connect('botdb.db')
        cursor = botdb.cursor()
        try:
            output = cursor.execute(query).fetchall()
            desc = ''
            if any(query.lower().startswith(val) for val in ['select', 'pragma']) and len(output) == 0:
                desc = 'No records found!'
            elif len(output) == 0:
                desc = 'Query executed successfully!'
            else:
                for _ in output:
                    desc += str(_) + '\n'

            embed = discord.Embed(title = 'Query Results:',
                                  description = '`' + desc + '`',
                                  color = discord.Color.teal())
            await ctx.send(embed = embed)

        except Exception as e:
            embed = discord.Embed(title = 'Command Error',
                                  description = str(e),
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
            botdb.rollback()

        finally:
            botdb.commit()
            botdb.close()
            
    @commands.command(hidden = True)
    @commands.is_owner()
    async def leave(self, ctx):
        """Leaves the Guild."""
        confirm = await ctx.send("`You really want me to leave this server?`")
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        def check(reaction, user):
            if user == ctx.message.author and any([str(reaction.emoji) == '✅', str(reaction.emoji) == '❌']):
                return True
        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout = 10.0, check = check)
        except asyncio.TimeoutError:
            await confirm.clear_reactions()
            await confirm.edit(content= "`Thank God! I don't have to leave this server.`")
        else:
            if str(reaction) == '✅':
                try:
                    await confirm.clear_reactions()
                    await confirm.edit(content= "`Goodbye!!! I'm leaving this server...`")
                    await ctx.guild.leave()
                except Exception as e:
                    await ctx.send(f"`{str(e)}`")
            elif str(reaction) == '❌':
                await confirm.clear_reactions()
                await confirm.edit(content= "`Thank You! I'm not gonna leave this server.`")


    @commands.command(hidden = True)
    @commands.is_owner()
    async def block(self, ctx, member: discord.Member):
        """Adds the member to the blocklist."""
        blocklist = self.db.get_collection("blocklist")
        mem = blocklist.find_one({"userid": member.id})
        if not mem:
            blocklist.insert_one({"userid": member.id})
            await ctx.send(f"{member.display_name} has been added to the blocklist!")
        else:
            await ctx.send(f"{member.display_name} is already blocked!")
        self.client.update_cache

    @commands.command(hidden = True)
    @commands.is_owner()
    async def unblock(self, ctx, member: discord.Member):
        """Removes the member from the blocklist."""
        blocklist = self.db.get_collection("blocklist")
        mem = blocklist.find_one({"userid": member.id})
        if mem:
            blocklist.delete_one({"userid": member.id})
            await ctx.send(f"{member.display_name} has been removed from the blocklist!")
        else:
            await ctx.send(f"{member.display_name} is not blocked!")
        self.client.update_cache



    @commands.command(hidden = True, name = 'uemoji')
    @commands.is_owner()
    async def upload_emoji(self, ctx, name: str, *, emoji: str):
        """Adds the emoji to bot database!"""
        try:
            mclient = MongoClient(os.environ.get('mongodb'))
            db = mclient.my_db
        except:
            return await ctx.send('Cannot connect to mongodb at the moment.')
        
        r = {'name' : name, 'emoji' : emoji.replace("`","")}
        table = db["emojis"]
        table.insert_one(r)
        self.client.update_cache
        await ctx.send(f"Emoji uploaded successfully!\n```{r}```")
        
    @commands.command(hidden = True, name = 'semo')
    @commands.is_owner()
    async def _send_emoji(self, ctx, name):
        """Sends the emoji from bot database."""
        emo = self.client.emotes.get(name, None)
        if emo:
            return await ctx.send(emo)
        return await ctx.send('`no emoji`')
        
    @commands.command(hidden = True, aliases = ["mystbin"])
    async def myst(self, ctx, * , text = ""):
        """Uploads your text to https://mystb.in/ and generates shareable link."""
        async with aiohttp.ClientSession() as session:
            pastedata = {"files":[{"content": text, "filename": "No Title"}]}
            async with session.put(url="https://api.mystb.in/paste", json=pastedata) as r:
                if r.status == 201:
                    mdata = await r.json()
                    await ctx.send(f"https://mystb.in/{mdata['id']}")
                else:
                    await ctx.send("FAIL")

    @commands.command(hidden = True, aliases = ['release', 'recycle'])
    async def _numbers(self, ctx, *, data = ""):
        """generates numbers to release/recycle the pokemons for @Pokemon#8738 bot."""
        if data:
            count = []
            for line in data.splitlines():
                x = line.split("|")[2].split(":")[1].replace(" ","")
                count.append(x)
            st = " ".join(count)
            embed = discord.Embed(title="Numbers:")
            embed.description = st
            await ctx.message.delete()
            await ctx.send(embed = embed)
        else:
            await ctx.message.delete()
            await ctx.send("No numbers")
    
    @commands.command(hidden = True, name = 'sync')
    @commands.is_owner()
    async def _sync(self, ctx):
        """sync app_commands globally"""
        await self.client.tree.sync()
        await ctx.send("Application commands synchronization successful!")

    # <# EliteBOY Command: Error Handler - Start #>

    @sql.error
    @enable.error
    @disable.error
    @load.error
    @unload.error
    @reload.error
    @leave.error
    @block.error
    @unblock.error
    @myst.error
    @_numbers.error
    @_sync.error
    async def owner_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            return
        elif isinstance(error, commands.CheckFailure):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, \nCommand Error: Please provide required command arguments!`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = f'Command Error: {str(error)}',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    # <# EliteBOY Command: Error Handler - End #>

async def setup(client):
    await client.add_cog(Owner(client))

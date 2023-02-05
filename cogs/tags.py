import discord, json, os, random
from pymongo import MongoClient
from discord.ext import commands

class Tags(commands.Cog):
    """Commands related to tags are here"""
    def __init__(self, client):
        self.client = client

    try:
        mclient = MongoClient(os.environ.get('mongodb'))
        db = mclient.get_database("my_db")
    except:
        print('Cannot connect to MongoDB at the moment!')


    @commands.group(aliases = ['t'])
    async def tag(self, ctx):
        """Displays tag contents. Also includes sub commands."""
        if ctx.invoked_subcommand is None:
            lst = ctx.message.content.split(maxsplit = 1)
            if len(lst) > 1:
                tagname = lst[1]
            else:
                tagname = ""
            #await ctx.send(tagname)
            tags = self.db.get_collection("tags")
            if tagname:
                tagname = tagname.lower()
                guildid = ctx.guild.id
                op = tags.find_one({"tagname": tagname, "guild": guildid})
            else:
                await ctx.send('`Please provide a tagname to display contents`', delete_after = 3)
                return
            if op:
                await ctx.send(op["tagcontent"])
            else:
                await ctx.send('`Tag not found!`')

    @tag.command(name = "create")
    @commands.check_any(commands.has_permissions(manage_messages = True), commands.is_owner())
    async def tag_create(self, ctx, *, tagdetails):
        """Creates a new tag. Ex: !tag create <tagname> || <tagcontent>"""
        tags = self.db.get_collection("tags")
        #result = [tag for tag in tags.find({'tagname': {'$regex': '.*'}})]

        if "||" in tagdetails:
            tagname, tagcontent = tagdetails.split("||", maxsplit = 1)
            tagname = tagname.lower().strip()
            tagcontent = tagcontent.strip()
            guildid = ctx.guild.id
        else:
            await ctx.send('`Invalid Command Usage! Use: tag create <tagname> || <tagcontents>`', delete_after=10)
            return

        invalidtags = ["create", "delete", "edit", "search", "info"]
        if any(tagname.startswith(nm) for nm in invalidtags):
            await ctx.send(f"```tagname cannot start with the following words: \n{', '.join(invalidtags)}```", delete_after = 5)
            return

        if len(tagname) > 25 or len(tagname) < 3:
            await ctx.send('`tagname must be 3 to 25 characters long!`', delete_after = 5)
            return

        if len(tagcontent) > 2000 or len(tagcontent) < 1:
            await ctx.send('`tag content must be 1 to 2000 characters long!`', delete_after = 5)
            return

        op = tags.find_one({"tagname": tagname, "guild": guildid})
        if not op:
            tags.insert_one({"tagname" : tagname, "tagcontent": tagcontent, "tagowner" : ctx.author.id, "guild": guildid})
            await ctx.send(f"{self.client.emotes.get('greentick','')} `Successfully created the tag: [{tagname}]`")
        else:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `[{tagname}] cannot be created as it already exists in the database!`")

    @tag.command(name = "search")
    async def tag_search(self, ctx, *, tagname):
        """Searches for a tag and displays results."""
        tags = self.db.get_collection("tags")
        tagname = tagname.lower()
        guildid = ctx.guild.id
        op = list(tags.find({'tagname': {'$regex': tagname}, "guild": guildid}))

        embed = discord.Embed(title=f"Search Results for: {tagname}")

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i: i + n]
        if op:
            page = chunks(op, 20)
            c = 1
            for p in page:
                desc = ""
                for r in p:
                    desc += f"{c}. [{r['tagname']}] - (ID: {str(r['_id'])[-6:]})\n"
                    c += 1
                if len(desc) > 4000:
                    desc = desc[:4000] + "\n..."

                embed.description = f"```{desc}```"
                embed.set_footer(text=f"Tag Search | Found {len(op)} tags matching your search criteria", icon_url=ctx.me.avatar_url)
                await ctx.send(embed = embed)
            
        else:
            embed.description = f"{self.client.emotes.get('alert','')} `Tag not found! Try searching for a part of the tagname?`"
            await ctx.send(embed = embed)


    @tag.command(hidden = True, name = "searchall")
    @commands.is_owner()
    async def tag_searchall(self, ctx, *, tagname):
        """Searches for a tag and displays results. -- owner only"""
        tags = self.db.get_collection("tags")
        tagname = tagname.lower()
        op = list(tags.find({'tagname': {'$regex': tagname}}))

        embed = discord.Embed(title=f"Search Results for: {tagname}")

        def chunks(lst, n):
            for i in range(0, len(lst), n):
                yield lst[i: i + n]
        if op:
            page = chunks(op, 20)
            c = 1
            for p in page:
                desc = ""
                for r in p:
                    desc += f"{c}. [{r['tagname']}] - (ID: {str(r['_id'])[-6:]})\n"
                    c += 1
                if len(desc) > 4000:
                    desc = desc[:4000] + "\n..."

                embed.description = f"```{desc}```"
                embed.set_footer(text=f"Tag Search | Found {len(op)} tags matching your search criteria", icon_url=ctx.me.avatar_url)
                await ctx.send(embed = embed)
            
        else:
            embed.description = f"{self.client.emotes.get('alert','')} `Tag not found! Try searching for a part of the tagname?`"
            await ctx.send(embed = embed)


    @tag.command(name = "edit")
    @commands.check_any(commands.has_permissions(manage_messages = True), commands.is_owner())
    async def tag_edit(self, ctx, *, tagdetails):
        """Edits the content of an existing tag. Ex: !tag edit <tagname> || <newtagcontents>"""
        tags = self.db.get_collection("tags")

        if "||" in tagdetails:
            tagname, tagcontent = tagdetails.split("||", maxsplit = 1)
            tagname = tagname.lower().strip()
            tagcontent = tagcontent.strip()
            guildid = ctx.guild.id
        else:
            await ctx.send('`Invalid Command Usage! Use: tag edit <tagname> || <newtagcontents>`', delete_after = 10)
            return

        if len(tagcontent) > 2000 or len(tagcontent) < 1:
            await ctx.send('`tag content must be 1 to 2000 characters long!`', delete_after = 5)
            return

        op = tags.find_one({"tagname": tagname, "guild": guildid})
        if op:
            if op['tagowner'] == ctx.author.id or ctx.author.id == self.client.ownerid:
                newval = {"$set" : {"tagname": tagname, "tagcontent": tagcontent, "tagowner": ctx.author.id, "guild":guildid}}
                tags.update_one({"tagname": tagname, "guild":guildid}, newval)
                await ctx.send(f"{self.client.emotes.get('greentick','')} `Successfully updated the tag [{tagname}]`")
            else:
                await ctx.send(f"{self.client.emotes.get('redtick','')} `You cannot edit/update the tag if you are not the owner of it.`")
        else:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Tag [{tagname}] doesn't exist!`")

    @tag.command(name = "delete")
    @commands.check_any(commands.has_permissions(manage_messages = True), commands.is_owner())
    async def tag_delete(self, ctx, *, tagname):
        """Deletes a tag."""
        tags = self.db.get_collection("tags")
        tagname = tagname.lower()
        guildid = ctx.guild.id
        op = tags.find_one({"tagname": tagname, "guild":guildid})
        if op:
            if op['tagowner'] == ctx.author.id or ctx.author.id == self.client.ownerid:
                tags.delete_one({"tagname": tagname, "guild":guildid})
                await ctx.send(f"{self.client.emotes.get('greentick','')} `Successfully deleted the tag [{tagname}]`")
            else:
                await ctx.send(f"{self.client.emotes.get('redtick','')} `You cannot delete the tag if you are not the owner of it.`")
        else:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Tag [{tagname}] doesn't exist!`")

    @tag.command(name = "info")
    @commands.check_any(commands.has_permissions(manage_messages = True), commands.is_owner())
    async def tag_info(self, ctx, *, tagname):
        """Shows information about the given tag."""
        tags = self.db.get_collection("tags")
        tagname = tagname.lower().strip()
        guildid = ctx.guild.id
        op = tags.find_one({"tagname": tagname, "guild":guildid})
        if op:
            user = self.client.get_user(op["tagowner"])
            embed = discord.Embed()
            if user:
                embed.set_author(name = user, icon_url=user.avatar_url)
            embed.title = f"Name: {op['tagname']}"
            embed.description = f"{op['tagcontent']}"
            embed.add_field(name="Owner:", value=f"{user.mention}", inline=True)
            embed.add_field(name="Guild ID:", value=f"{guildid}", inline=True)
            embed.add_field(name="Tag ID:", value=f"{str(op['_id'])[-6:]}", inline=True)
            embed.set_footer(text = f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Tag [{tagname}] doesn't exist!`")

    @tag.command(hidden = True, name = "infoall")
    @commands.is_owner()
    async def tag_infoall(self, ctx, *, tagname):
        """Shows information about the given tag. -- owner only"""
        tags = self.db.get_collection("tags")
        tagname = tagname.lower().strip()
        guildid = ctx.guild.id
        op = tags.find_one({"tagname": tagname})
        if op:
            user = self.client.get_user(op["tagowner"])
            embed = discord.Embed()
            if user:
                embed.set_author(name = user, icon_url=user.avatar_url)
            embed.title = f"Name: {op['tagname']}"
            embed.description = f"{op['tagcontent']}"
            embed.add_field(name="Owner:", value=f"{user.mention}", inline=True)
            embed.add_field(name="Guild ID:", value=f"{guildid}", inline=True)
            embed.add_field(name="Tag ID:", value=f"{str(op['_id'])[-6:]}", inline=True)
            embed.set_footer(text = f"Requested by: {ctx.author}", icon_url=ctx.author.avatar_url)
            await ctx.send(embed=embed)
        else:
            await ctx.send(f"{self.client.emotes.get('redtick','')} `Tag [{tagname}] doesn't exist!`")

    # <# Other Error Handler - Start #>

    @tag.error
    @tag_create.error
    @tag_search.error
    @tag_searchall.error
    @tag_edit.error
    @tag_delete.error
    @tag_info.error
    @tag_infoall.error
    async def tags_error(self, ctx, error):
        if isinstance(error, commands.DisabledCommand):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, Please provide required arguments for {ctx.command.name} command!`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CommandOnCooldown):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, You are on cooldown. Please retry after {round(error.retry_after)}s.`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.CheckFailure):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, You cannot use this command as: {str(error)}`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        elif isinstance(error, commands.BotMissingPermissions):
            embed = discord.Embed(description = f'`Hi {ctx.author.name}, I do not have the following permissions: {error.missing_perms}`',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)
        else:
            embed = discord.Embed(description = str(error), color = discord.Color.red())
            await ctx.send(embed = embed)

    # <# Other Error Handler - Start #>

async def setup(client):
    await client.add_cog(Tags(client))
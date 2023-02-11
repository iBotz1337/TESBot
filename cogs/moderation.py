import discord, asyncio
from discord.ext import commands

class Moderation(commands.Cog):

    def __init__(self, client):
        self.client = client

    @commands.command(aliases = ['purge', 'del', 'clear'])
    @commands.check_any(commands.has_permissions(manage_messages = True), commands.is_owner())
    @commands.guild_only()
    async def delete(self, ctx, lim: int = 10):
        """Deletes the given number of messages from current channel."""
        await ctx.message.delete()
        if lim <= 100:
            purged_messages = await ctx.channel.purge(limit = lim)
            embed = discord.Embed(description = f'Hello {ctx.message.author.display_name},\n{len(purged_messages)} messages have been deleted from {ctx.channel.mention}.')
            x = await ctx.send(embed = embed)
            await asyncio.sleep(3)
            await x.delete()
        else:
            embed = discord.Embed(description = f'Hello {ctx.message.author.display_name},\nOnly a maximum of 100 messages can be deleted at a time!',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    @commands.command(aliases = [])
    @commands.check_any(commands.has_permissions(kick_members = True), commands.is_owner())
    @commands.guild_only()
    async def kick(self, ctx, member: discord.Member, *, reason = None):
        """Kicks the member out of the server."""
        embed = discord.Embed(description = f'Confirmation Required: You are about to `Kick`: `{member}`!\n\n`Please confirm by reacting to this message.`',
                              color = discord.Color.teal())
        confirm = await ctx.send(embed = embed)
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        def check(reaction, user):
            if user == ctx.message.author and any([str(reaction.emoji) == '✅', str(reaction.emoji) == '❌']):
                return True

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout = 15.0, check = check)
        except asyncio.TimeoutError:
            embed = discord.Embed(description = 'Confirmation failed due to timeout!',
                                  color = discord.Color.red())
            await confirm.clear_reactions()
            await confirm.edit(embed = embed)
        else:
            if str(reaction) == '✅':
                try:
                    await member.kick(reason = reason)
                    embed = discord.Embed(description = f'`{member}` has been `Kicked` out of the server!',
                                          color = discord.Color.teal())
                    await confirm.clear_reactions()
                    await confirm.edit(embed = embed)
                except Exception as e:
                    embed = discord.Embed(description = f'Command Error:\n`{str(e)}`!',
                                          color = discord.Color.red())
                    await confirm.clear_reactions()
                    await confirm.edit(embed = embed)
            elif str(reaction) == '❌':
                embed = discord.Embed(description = f'`Kick` command is cancelled by {ctx.author.mention}!',
                                      color = discord.Color.red())
                await confirm.clear_reactions()
                await confirm.edit(embed = embed)

    @commands.command(aliases = [])
    @commands.check_any(commands.has_permissions(ban_members = True), commands.is_owner())
    @commands.guild_only()
    async def ban(self, ctx, member: discord.Member, *, reason = None):
        """Bans the member from the server."""
        embed = discord.Embed(description = f'Confirmation Required: You are about to `Ban`: `{member}`!\n\n`Please confirm by reacting to this message.`',
                              color = discord.Color.teal())
        confirm = await ctx.send(embed = embed)
        await confirm.add_reaction('✅')
        await confirm.add_reaction('❌')

        def check(reaction, user):
            if user == ctx.message.author and any([str(reaction.emoji) == '✅', str(reaction.emoji) == '❌']):
                return True

        try:
            reaction, user = await self.client.wait_for('reaction_add', timeout = 15.0, check = check)
        except asyncio.TimeoutError:
            embed = discord.Embed(description = 'Confirmation failed due to timeout!',
                                  color = discord.Color.red())
            await confirm.clear_reactions()
            await confirm.edit(embed = embed)
        else:
            if str(reaction) == '✅':
                try:
                    await member.ban(reason = reason)
                    embed = discord.Embed(description = f'`{member}` has been `Banned` from this server!',
                                          color = discord.Color.teal())
                    await confirm.clear_reactions()
                    await confirm.edit(embed = embed)
                except Exception as e:
                    embed = discord.Embed(description = f'Command Error:\n`{str(e)}`!',
                                          color = discord.Color.red())
                    await confirm.clear_reactions()
                    await confirm.edit(embed = embed)
            elif str(reaction) == '❌':
                embed = discord.Embed(description = f'`Ban` command is cancelled by {ctx.author.mention}!',
                                      color = discord.Color.red())
                await confirm.clear_reactions()
                await confirm.edit(embed = embed)

    @commands.command(aliases = [])
    @commands.check_any(commands.has_permissions(ban_members = True), commands.is_owner())
    @commands.guild_only()
    async def unban(self, ctx, *, member: discord.Member):
        """Unbans the member from the server."""
        if member in ctx.guild.bans():
            embed = discord.Embed(description = f'Confirmation Required: You are about to `Unban`: `{member}`!\n\n`Please confirm by reacting to this message.`',
                                  color = discord.Color.teal())
            confirm = await ctx.send(embed = embed)
            await confirm.add_reaction('✅')
            await confirm.add_reaction('❌')

            def check(reaction, user):
                if user == ctx.message.author and any([str(reaction.emoji) == '✅', str(reaction.emoji) == '❌']):
                    return True

            try:
                reaction, user = await self.client.wait_for('reaction_add', timeout = 10.0, check = check)
            except asyncio.TimeoutError:
                embed = discord.Embed(description = 'Confirmation failed due to timeout!',
                                      color = discord.Color.red())
                await confirm.clear_reactions()
                await confirm.edit(embed = embed)
            else:
                if str(reaction) == '✅':
                    try:
                        await member.unban()
                        embed = discord.Embed(description = f'`{member}` has been `Unbanned` from this server!',
                                              color = discord.Color.teal())
                        await confirm.clear_reactions()
                        await confirm.edit(embed = embed)
                    except Exception as e:
                        embed = discord.Embed(description = f'Command Error:\n`{str(e)}`!',
                                              color = discord.Color.red())
                        await confirm.clear_reactions()
                        await confirm.edit(embed = embed)
                elif str(reaction) == '❌':
                    embed = discord.Embed(description = f'`Unban` command is cancelled by {ctx.author.mention}!',
                                          color = discord.Color.red())
                    await confirm.clear_reactions()
                    await confirm.edit(embed = embed)
        else:
            embed = discord.Embed(description = f'Hello {ctx.message.author.mention}, This command can only be used to unban `Banned` members!',
                                  color = discord.Color.red())
            await ctx.send(embed = embed)

    # <# Moderation Error Handler - Start #>

    @delete.error
    @kick.error
    @ban.error
    @unban.error
    async def moderation_error(self, ctx, error):
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

    # <# Moderation Error Handler - End #>


async def setup(client):
    await client.add_cog(Moderation(client))
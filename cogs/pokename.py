import discord, os, random, requests, async_cse, asyncio, io
from datetime import datetime
from discord.ext import commands, menus
from pymongo import MongoClient

class Pokename(commands.Cog):

    def __init__(self, client):
        self.client = client

    try:
        mclient = MongoClient(os.environ.get('mongodb'))
        db = mclient.get_database("my_db")
    except:
        print('Cannot connect to MongoDB at the moment!')


    @commands.command(aliases = ["itz", "this"])
    @commands.guild_only()
    async def _teach(self, ctx, *, pokemon = ""):
        """Reply to the pokemon bot spawn and type @EliteBOT itz <pokemon>"""

        if ctx.author.id not in self.client.tutors:
            return

        try:
            ref = ctx.message.reference
            if ref and isinstance(ref.resolved, discord.Message):
                ref_author = ref.resolved.author.id
                ref_embeds = ref.resolved.embeds

                #check if the reference is Pokemon bot spawn.
                if ref_author == 669228505128501258 and ref_embeds:
                    wildPoke = ref_embeds[0].to_dict()
                    if "Guess the pokémon" in str(wildPoke):
                        ref_image_url = ref_embeds[0].image.url
                        pokename = self.db.get_collection("pokename")
                        poke_record = pokename.find_one({"name": "all_mons"})

                        if pokemon.lower() in poke_record["value"]:
                            imghash = self.client.hashit(ref_image_url)
                            if imghash:
                                record = pokename.find_one({"hash_id": imghash})
                                if not record:
                                    pokename.insert_one({"hash_id" : imghash, "name": pokemon, "tutor" : ctx.author.id})
                                    await ctx.send(f"{self.client.emotes.get('greentick','')} `[{pokemon}] : {imghash}`")

                                else:
                                    await ctx.send(f"Record already exists in the database:\n```{record}```")

                            else:
                                await ctx.send(f"{self.client.emotes.get('redtick','')}`Unable to hash the image! Please try again later...`")

                        else:
                            await ctx.send(f"{self.client.emotes.get('redtick','')}`{pokemon.title()}: This is not a valid pokemon.`")
                    else:
                        await ctx.send(f"{self.client.emotes.get('redtick','')}`This is not a Pokemon bot spawn.`")
                        
                else:
                    await ctx.send(f"{self.client.emotes.get('redtick','')}`This message doesn't have an ebmed or it's not from Pokemon bot.`")
            else:
                await ctx.send(f"{self.client.emotes.get('redtick','')}`Invalid reference...`")

        except Exception as e:
            print(str(e))

    
    @_teach.error
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

    # <# Pokename Error Handler - End #>

async def setup(client):
    await client.add_cog(Pokename(client))
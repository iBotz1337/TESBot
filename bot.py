import os, discord, asyncio
from discord.ext import commands
from datetime import datetime
from pymongo import MongoClient
import secret

try:
    mclient = MongoClient(os.environ.get('mongodb'))
    db = mclient.get_database("my_db")
except:
    print('Cannot connect to MongoDB at the moment!')

class MyBot(commands.Bot):
    #Declare Bot variables here (can be accesses in cogs using self.client.variable)
    launch_time = datetime.utcnow()
    wtpList = []
    activeQuiz = []
    snipes = {}
    esnipes = {}
    disabledCogs = ['cogs.test']
    ownerid = 510664110669561856
    inviteurl = ""
    boxrateconfig = {"base": 1, "unbase": 0.8, "other": 5}
    raids_config = {'category_id': 1043874022552780880, 
                    'channel_id': 1071627979110760499, 
                    'doable_raids': ['articuno', 'mew', 'mewtwo', 'celebi', 'deoxys', 'uxie', 'mesprit', 'azelf', 'cresselia', 'heatran', 'phione', 'manaphy', 'shaymin', 'virizion', 'genesect', 'keldeo', 'diancie', 'hoopa', 'tapu lele', 'lunala', 'nihilego', 'pheromosa', 'kartana', 'necrozma', 'poipole', 'naganadel', 'stakataka', 'blacephalon', 'xurkitree', 'melmetal', 'zarude', 'calyrex', 'enamorus', 'wo-chien', 'chien-pao', 'chi-yu', 'rapid strike style urshifu', 'gigantamax rapid strike style urshifu', 'single strike urshifu']}    
    
    def __init__(self, command_prefix, intents):
        super().__init__(command_prefix=command_prefix, intents=intents)
        self._cache_block = None
        self._cache_emoji = None
        
    @property
    def emotes(self):
        if self._cache_emoji is None:
            records = db.emojis.find()
            self._cache_emoji = {r['name'] : r['emoji'] for r in records}
        return self._cache_emoji
        
    @property
    def blocklist(self):
        if self._cache_block is None:
            records = db.blocklist.find()
            self._cache_block = [r['userid'] for r in records]
        return self._cache_block
        
    @property
    def update_cache(self):
        self._cache_emoji = {r['name'] : r['emoji'] for r in db.emojis.find()}
        self._cache_block = [r['userid'] for r in db.blocklist.find()]
        return "`Updated the cache`"

    @property
    def get_time(self):
        return datetime.now().strftime("%d %b, %Y | %I:%M:%S %p")
        
async def get_prefix(client, message):
    if not message.guild:
        return commands.when_mentioned_or(*("",))(client, message)
    prefixes = db.get_collection("prefixes")
    p = prefixes.find_one({"serverid": message.guild.id})
    if p:
        pf = p["prefix"]
        return commands.when_mentioned_or(*(pf,))(client, message)
    else:
        prefixes.insert_one({"serverid": message.guild.id, "prefix" : "!"})
        return commands.when_mentioned_or(*("!",))(client, message)
        
# Creating the Bot using MyBot class
client = MyBot(command_prefix = get_prefix, intents = discord.Intents.all())

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.online, activity = discord.Game('Pokemon Creed!'))
    print('The Bot is online.')

@client.event
async def on_message(message):
    channel = message.channel
        
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != client.ownerid:
            return

    if message.channel.category_id == client.raids_config["category_id"]:
        if message.embeds:
            embed = message.embeds[0]
            if "Raid Announcement" in embed.title:
                description = embed.description
                raid_boss = description.splitlines()[1].split(":**", maxsplit=1)[1].lower().strip()
                if raid_boss in client.raids_config["doable_raids"]:
                    embed = discord.Embed(title= "⚔️ Raid Announcement ⚔️", description=description, url = message.jump_url, color = discord.Color.teal())
                    embed.add_field(name="Channel:", value=f"{message.channel.mention}")
                    channel_id = client.get_channel(client.raids_config["channel_id"])
                    await channel_id.send(embed=embed)

    if message.author.bot or message.author.id in client.blocklist:
        return 

    if client.user in message.mentions and message.content.lower().startswith(('hey', 'hi', 'hello', 'yo')):
        prefix = await client.get_prefix(message)
        desc = f"My prefix in this server is {client.emotes.get('arrowright','')} **{', '.join(prefix[2:])}** {client.emotes.get('arrowleft','')}"
        embed = discord.Embed(description = desc)
        embed.set_author(name=f'Hello {message.author.display_name}', icon_url=message.author.avatar_url)
        await channel.send(embed = embed)

    await client.process_commands(message)


# <# Run the Bot - Start #>
os.environ["JISHAKU_NO_UNDERSCORE"]="True"
os.environ["JISHAKU_HIDE"]="True"


async def main():
    extensions = ['cogs.basic', 'cogs.error', 'cogs.games', 'cogs.moderation', 'cogs.tags', 'cogs.owner', 'cogs.pokemoncreed', 'cogs.test', 'jishaku']
    async with client:
        for extension in extensions:
            if extension not in client.disabledCogs:
                await client.load_extension(extension)
                print(f'Successfullly loaded [{extension}] extension!')
        await client.start(os.environ.get('TOKEN'))

asyncio.run(main())

# <# Run the Bot - End #>

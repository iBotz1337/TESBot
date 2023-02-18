import os, discord, asyncio, requests, shutil, hashlib, io
from discord.ext import commands
from datetime import datetime
from pymongo import MongoClient
from discord import app_commands
from PIL import Image
#import secret

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
    tutors = [510664110669561856]
    inviteurl = ""
    boxrateconfig = {"base": 1, "unbase": 0.8, "other": 5}
    raids_config = {'category_id': [1043874022552780880, 1065988552338452501], 
                    '10_shards_raids_ch': 1071627979110760499,
                    '2_shards_raids_ch': 1072353312164298833,
                    '10_shards_raids': ['articuno', 'mew', 'mewtwo', 'celebi', 'deoxys', 'uxie', 'mesprit', 'azelf', 'cresselia', 'heatran', 'phione', 'manaphy', 'shaymin', 'virizion', 'genesect', 'keldeo', 'diancie', 'hoopa', 'tapu lele', 'lunala', 'nihilego', 'pheromosa', 'kartana', 'necrozma', 'poipole', 'naganadel', 'stakataka', 'blacephalon', 'xurkitree', 'melmetal', 'zarude', 'calyrex', 'enamorus', 'wo-chien', 'chien-pao', 'chi-yu', 'rapid strike style urshifu', 'gigantamax rapid strike style urshifu', 'single strike urshifu'],
                    '2_shards_raids': ['alolan rattata', 'alolan raticate', 'alolan sandshrew', 'alolan vulpix', 'alolan ninetales', 'alolan diglett', 'alolan meowth', 'alolan persian', 'alolan geodude', 'galarian meowth', 'galarian ponyta', 'galarian slowpoke', 'galarian zigzagoon', 'galarian linoone', 'galarian darumaka', 'hisuian growlithe', 'hisuian voltorb', 'hisuian sneasel', 'hisuian lilligant', 'hisuian decidueye']
                    }    
    
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
    
    @classmethod
    def hashit(self, img_url):
        r = requests.get(img_url, stream=True)
        imghash = None
        try:
            #download if its able to/output error if not
            if r.status_code == 200:
                r.raw.decode_content = True
                with open("./files/spawn.png", "wb") as f:
                    shutil.copyfileobj(r.raw, f)
            else:
                print("Image Couldn't be retreived")
            #hash imgage
            img = Image.open("./files/spawn.png")
            m = hashlib.md5()
            with io.BytesIO() as memf:
                img.save(memf, "PNG")
                data = memf.getvalue()
                m.update(data)
                imghash = m.hexdigest()
        except Exception as e:
            print(str(e))
            
        return imghash
        
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


@client.tree.command(name="ping", description="shows the bot latency.")
async def _ping(interaction: discord.Interaction):
    await interaction.response.send_message(f"{client.emotes.get('typing','')} `Pong! {round(client.latency * 1000, 2)}ms.`")

@client.event
async def on_ready():
    await client.change_presence(status = discord.Status.idle, activity = discord.Game('Pokemon!'))
    #await client.change_presence(status = discord.Status.dnd, activity = discord.Game('with EliteBOY'))
    print('The Bot is online.')

@client.event
async def on_message(message):
    channel = message.channel
        
    if isinstance(message.channel, discord.DMChannel):
        if message.author.id != client.ownerid:
            return

    if message.channel.category_id in client.raids_config["category_id"]:
        if message.embeds:
            embed = message.embeds[0]
            if "Raid Announcement" in embed.title:
                description = embed.description
                raid_boss = description.splitlines()[1].split(":**", maxsplit=1)[1].lower().strip()

                if raid_boss in client.raids_config["10_shards_raids"]:
                    embed = discord.Embed(title= "⚔️ Raid Announcement ⚔️", description=description, url = message.jump_url, color = discord.Color.teal())
                    embed.add_field(name="Channel:", value=f"{message.channel.mention}")
                    channel_id = client.get_channel(client.raids_config["10_shards_raids_ch"])
                    await channel_id.send(embed=embed)

                elif raid_boss in client.raids_config["2_shards_raids"]:
                    embed = discord.Embed(title= "⚔️ Raid Announcement ⚔️", description=description, url = message.jump_url, color = discord.Color.yellow())
                    embed.add_field(name="Channel:", value=f"{message.channel.mention}")
                    channel_id = client.get_channel(client.raids_config["2_shards_raids_ch"])
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
    extensions = ['cogs.basic', 'cogs.error', 'cogs.games', 'cogs.moderation', 'cogs.tags', 'cogs.owner', 'cogs.pokemoncreed', 'cogs.pokename', 'jishaku']
    async with client:
        for extension in extensions:
            if extension not in client.disabledCogs:
                await client.load_extension(extension)
                print(f'Successfullly loaded [{extension}] extension!')
        await client.start(os.environ.get('TOKEN'))

asyncio.run(main())

# <# Run the Bot - End #>

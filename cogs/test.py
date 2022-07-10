from discord.ext import commands, menus
from pymongo import MongoClient

class Test(commands.Cog):
    """Used to test new commands"""
    def __init__(self, client):
        self.client = client

    pass
    
                
def setup(client):
    client.add_cog(Test(client))
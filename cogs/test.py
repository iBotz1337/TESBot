import asyncio
from random import random
from sre_constants import SUCCESS
import aiohttp
from discord.ext import commands, menus
from pymongo import MongoClient
import discord, mechanicalsoup, json, aiohttp, os, requests

class Test(commands.Cog):
    """Used to test new commands"""
    def __init__(self, client):
        self.client = client


async def setup(client):
    await client.add_cog(Test(client))
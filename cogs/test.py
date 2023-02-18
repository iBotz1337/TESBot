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

    @commands.command()
    async def pong(self, ctx):
        """Displays Bot latency."""
        await ctx.send(f"{self.client.emotes.get('typing','')} `Pong! {round(self.client.latency * 1000, 2)}ms.`")


async def setup(client):
    await client.add_cog(Test(client))
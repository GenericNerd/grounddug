# GroundDug

import discord
from discord.ext import commands
from discord.ext import tasks
import asyncio
import cogs.utils.db as db
from bson.objectid import ObjectId
import dbl
import httpx
import os

environment = os.getenv("GD_ENV","beta")
httpxClient = httpx.AsyncClient()

class DirectoryListings(commands.Cog):
    """
    Handles interactions with Discord Direcotory Listings GroundDug is in
    This includes top.gg, DiscordBots, BotsForDiscord etc
    """
    
    def __init(self,bot):
        self.bot = bot
        # Bot List API keys to interact with the websites
        self.topGGAPI = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjU1MzYwMjM1Mzk2MjU0OTI0OSIsImJvdCI6dHJ1ZSwiaWF0IjoxNTkzODg2NTg3fQ.B3Ur3HFLz3M89jzrl0BmTB2yFN9c0RCJq57NovRnY2M"
        self.discordBotsAPI = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhcGkiOnRydWUsImlkIjoiMTc5MjkyMTYyMDM3NTE0MjQxIiwiaWF0IjoxNTkzODg3MDY2fQ.U-tsOONaxP0RKRh2mf-V0_PyrDFEtGsC7Jqd_FWKZ0Q"
        self.botsForDiscordAPI = "251b7801f049d5dc856ee9d308f2dfadd8870ea398651eb8266b00ba91270b99f06164a60768f80bfaf6a176899e762ef5a2d3f738e7c557406eb2bd5e06c656"
        self.discordBotListAPI = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0IjoxLCJpZCI6IjU1MzYwMjM1Mzk2MjU0OTI0OSIsImlhdCI6MTU5Mzg5MDMxNH0.23nL24HvIh_deQNwA-h222g9xoShKKK1PDU3mOjHE48"
        self.dblpy = dbl.Client(self.bot, self.topGGAPI)
        self.updateStats.start()

    @tasks.loop(minutes=60)
    async def updateStats(self):
        # Only update APIs if current environment is production
        if environment == "production":
            shards = len(self.bot.latencies)
            guilds = len(self.bot.guilds)
            settings = await db.find("settings", {"_id": ObjectId("5e18fd4d123a50ef10d8332e")})
            # Discord Bots API
            headers = {"Countent-Type": "application/json", "Authorization": self.discordBotsAPI, "User-Agent": "GroundDug-2658/Beta-v1.2 (DPY; +https://grounddug.xyz/) DBots/553602353962549249"}
            async with httpx.ClientSession(headers=headers) as session:
                data = {"shardCount": shards, "guildCount": guilds}
                session.post("https://discord.bots.gg/api/v1/bots/553602353962549249/stats", json=data)
            # BotsForDiscord API
            headers["Authorization"] = self.botsForDiscordAPI
            del headers["User-Agent"]
            async with httpx.ClientSession(headers=headers) as session:
                data = {"server_count": guilds}
                session.post("https://botsfordiscord.com/api/bot/553602353962549249", json=data)
            # DiscordBotList API
            headers["Authorization"] = self.discordBotsAPI
            async with httpx.ClientSession(headers=headers) as session:
                data = {"guilds": guilds, "users": settings["userCount"]}
            await self.dblpy.post_guild_count()

def setup(bot):
    bot.add_cog(DirectoryListings(bot))
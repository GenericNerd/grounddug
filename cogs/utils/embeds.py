#GroundDug Embed Handler

import discord
import asyncio

async def generate(title,description,cl=None):
    embed = discord.Embed(title=title,description=description)
    if cl is None:
        embed.color = 0x0088ff
    else:
        embed.color = cl
    embed.set_footer(text="GroundDug | 2020",icon_url="https://cdn.discordapp.com/avatars/553602353962549249/641fcc61b43b5ce4b4cbe94c8c0270fa.webp?size=128")
    return embed

async def add_field(embed,name,value=None,inline=False):
    if value == None:
        embed.add_field(name=name,value="\u200b",inline=inline)
    else:
        embed.add_field(name=name,value=value,inline=inline)
    return embed

async def error(ctx,error):
    await ctx.send(embed=(await generate("Something went wrong!",f"`{error}`",0xff0000)))
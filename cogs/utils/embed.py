# GroundDug Embed Generator

import discord
import asyncio

# Generate a discord.Embed object
async def generate(title,description,color=None):
    # Create an embed with the title and description as parsed
    embed = discord.Embed(title=title,description=description)
    # Give normal color or custom color, depending if color is None
    if color is None:
        embed.color = 0x0088ff
    else:
        embed.color = color
    # Give embed a footer with the GD icon
    embed.set_footer(text="GroundDug | 2020",icon_url="https://cdn.discordapp.com/avatars/553602353962549249/641fcc61b43b5ce4b4cbe94c8c0270fa.webp?size=128")
    return embed

# Add a field to the embed
async def add_field(embed,name,value=None,inline=False):
    # Check is value parsed is none
    if value is None:
        # Make an empty value field
        embed.add_field(name=name,value="\u200b",inline=inline)
    else:
        embed.add_field(name=name,value=value,inline=inline)
    return embed

async def error(ctx,error):
    # Generate an embed with the color red with value error
    await ctx.send(embed=(await generate("Something went wrong!",f"`{error}`",0xff0000)))
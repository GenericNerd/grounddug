#PXB Core

# # # # # # # # # #
# LIBRARY IMPORTS #
# # # # # # # # # #

import discord 
from discord.ext import commands 
import asyncio 
import os
import json
from datetime import datetime
#import psutil

# # # # # # #
# VARIABLES #
# # # # # # #

botToken = None
developers = None
# translations = None
startUpExtensions = ["admin"]
bot = commands.Bot(command_prefix="!")
cwd = os.getcwd()

# # # # # # #
# FUNCTIONS #
# # # # # # #

def getSettings(filejson):
    with open(filejson,"r",encoding="UTF-8") as file:
        settings = json.loads(file.read())
        global botToken,developers
        botToken = settings["bot_info"]["token"]
        developers = settings["badges"]["developers"]

async def checkDev(ctx):
    if ctx.author.id in developers:
        return True
    else:
        return False

async def error(ctx,error):
    msg = await ctx.send(embed=discord.Embed(title="The command you have entered is invalid",description=f"{ctx.message.content} `{error}`",color=0xff0000).set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
    await asyncio.sleep(5)
    await msg.delete()

async def reloadall():
	modules = []
	for extension in os.listdir(cwd):
		if os.path.isfile(extension):
			if extension[-3:] == ".py":
				if extension[:-3] != "starter" or extension[:-3] != "pxb":
					module = extension[:-3]
					modules.append(module)
	embed = discord.Embed(title="Restarted modules",description=f"The following modules have been restarted:")
	for module in modules:
		bot.unload_extension(module)
		bot.load_extension(module)
		embed.add_field(name=module,value="✅",inline=True)
	return embed

async def usercheck(ctx,user):
    roles = []
    embed = discord.Embed(title=f"{user.name}#{user.discriminator}",description=user.mention).set_thumbnail(url=user.avatar_url).set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC - {user.id}")
    embed.add_field(name="Discord status",value=user.status,inline=True)
    embed.add_field(name="Server join date",value=f"{user.joined_at} `{str(datetime.utcnow()-user.joined_at).split('.')[0]} ago`",inline=True)
    embed.add_field(name="ID",value=user.id,inline=False)
    embed.add_field(name="Account age",value=str(datetime.utcnow()-user.created_at).split('.')[0],inline=True)
    for role in user.roles:
        if role.name != "@everyone":
            roles.append(role.name)
    if roles == []:
        embed.add_field(name="Roles",value="No roles",inline=False)
    else:
        embed.add_field(name="Roles",value=roles,inline=False)
    embed.add_field(name="Server permissions",value=user.guild_permissions,inline=False)
    await ctx.send(embed=embed)

# # ## # #
# EVENTS #
# # ## # #

@bot.event
async def on_ready():
    print(f"\n\033[0;36;40m[{bot.user.name}]\033[0;37;40m Started")
    with open("botlogs.txt","a+",encoding="UTF-8") as file:
        file.write(f"[{str(datetime.utcnow())[:-7]}] [{bot.user.name}] Started\n")

@bot.event
async def on_command(ctx):
    await ctx.message.delete()

# # # # # ## # # # # #
# NO MODULE COMMANDS #
# # # # # ## # # # # #

@bot.command(name="userinfo",description="Returns information regarding a specific user")
async def userinfo(ctx,user:discord.Member):
    await usercheck(ctx,user)
@userinfo.error
async def userinfo_handler(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        if error.param.name == "user":
            await usercheck(ctx,ctx.author)

@bot.command(name="serverinfo",description="Returns information regarding the server")
async def serverinfo(ctx):
    #FIX THIS IT SEEMS BROKEN HELPPPPPPPPP
    guild = ctx.guild
    embed = discord.Embed(title=f"{guild.name} information").set_thumbnail(url=guild.icon_url)
    embed.add_field(name="Members",value=f"Currently {guild.member_count} members",inline=True).set_footer(text=f"{guild.id} / Large guild: {guild.large}")
    embed.add_field(name="Server age",value=f"{str(datetime.utcnow()-guild.created_at).split('.')[0]} ago",inline=True)
    embed.add_field(name="Owner",value=f"{guild.owner} `{guild.owner_id}`",inline=True)

# @bot.command(name="botinfo",description="Returns information regarding the bot")
# async def botinfo(ctx):
#     embed = discord.Embed(title=f"{bot.user.name} information",description=f"Information about {bot.user.name}").set_footer(text=str(datetime.utcnow())[:-7])
#     embed.add_field(name="discord.py version",value=f"discord.py version {discord.__version__}",inline=True)
#     embed.add_field(name="CPU usage",value=f"{psutil.cpu_percent()}%",inline=True)
#     embed.add_field(name="RAM usage",value=f"{psutil.virtual_memory().used}MB/{psutil.virtual_memory().total}MB",inline=True)
#     embed.add_field(name="System uptime",value=f'Since {datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S")} BST',inline=True)
#     embed.add_field(name="Operating system",value="Windows 10, build 1708, Home Edition",inline=True)
#     await ctx.send(embed=embed)

# bot.remove_command("help")
# @bot.command(name="help",description="Help yourself")
# async def help(ctx):

# # # # ## # # # #
# COMMAND GROUPS #
# # # # ## # # # #

@bot.group(name="developer",description="Developer commands",hidden=True)
@commands.check(checkDev)
async def developer(ctx):
    if ctx.invoked_subcommand is None:
        await error(ctx,"NO_INVOKED_SUBCOMMAND")

@bot.group(name="modules",description="Module management",hidden=True)
@commands.check(checkDev)
async def modules(ctx):
    if ctx.invoked_subcommand is None:
        await error(ctx,"NO_INVOKED_SUBCOMMAND")
 
# # # # ## # # # #
# DEVELOPER CMDS #
# # # # ## # # # #

@developer.command(name="restart",description="Restart the bot")
async def _restart(ctx):
    await ctx.message.delete()
    with open("botlogs.txt","a+",encoding="UTF-8") as file:
        file.write(f"[{str(datetime.utcnow())[:-7]}] [{bot.user.name}] Restart invoked by {ctx.author.name}#{ctx.author.discriminator}\n")
    await ctx.send(embed=discord.Embed(title="Bot is restarting").set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
    os._exit(100)

@developer.command(name="shutdown",description="Shuts down the bot")
async def _shutdown(ctx,time:int):
    msg = await ctx.send(embed=discord.Embed(title=f"Shutting down in {time}s",color=0xff0000))
    print(f"\n\033[0;36;40m[{bot.user.name}]\033[0;37;40m Shutdown invoked by\033[0;32;40m {ctx.author.name}#{ctx.author.discriminator}\033[0;37;40m at\033[0;32;40m {str(datetime.utcnow())[:-7]}\033[0;37;40m")
    with open("botlogs.txt","a+",encoding="UTF-8") as file:
        file.write(f"[{str(datetime.utcnow())[:-7]}] [{bot.user.name}] Shutdown invoked by {ctx.author.name}#{ctx.author.discriminator}\n")
    time=time-1
    while time != 0:
        await msg.edit(embed=discord.Embed(title=f"Shutting down in {time}s",color=0xff0000))
        time=time-1
        await asyncio.sleep(1)
    await bot.logout()
    os._exit(0)
@_shutdown.error
async def _shutdown_handler(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        if error.param.name == "time":
            await error(ctx,"NO_TIME_ATTRIBUTED")

@developer.command(name="eval")
async def _eval(ctx,cmd:str):
    try:
        result = (await eval(cmd))
    except:
        result = (eval(cmd))
    await ctx.send(result)

# # # #  # # # #
# MODULES CMDS #
# # # #  # # # #

@modules.command(name="reload",description="Reload one module")
async def _reload(ctx,module:str):
    bot.unload_extension(module)
    bot.load_extension(module)
    await ctx.send(embed=discord.Embed(title=f"Module {module} has been reloaded successfully").set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
@_reload.error
async def _reload_handler(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        if error.param.name == "module":
            await error(ctx,"NO_CALLED_MODULE")

@modules.command(name="reloadall",aliases=["rea"],description="Reloads all modules")
async def _reloadall(ctx):
    embed = await reloadall()
    await ctx.send(embed=embed)

@modules.command(name="unload",description="Unload a specific module")
async def _unload(ctx,module):
    bot.unload_extension(module)
    await ctx.send(embed=discord.Embed(title=f"The module {module} has been unloaded").set_footer(text=f"{str(datetime.utcnow())[:-7]} UTC"))
@_unload.error
async def _unload_handler(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        if error.param.name == "module":
            await error(ctx,"NO_CALLED_MODULE")

@modules.command(name="load",description="Load a specific module")
async def _load(ctx,module):
    bot.load_extension(module)
    await ctx.send(embed=discord.Embed(title=f"The module {module} has been loaded"))
@_load.error
async def _load_handler(ctx,error):
    if isinstance(error,commands.MissingRequiredArgument):
        if error.param.name == "module":
            await error(ctx,"NO_CALLED_MODULE")

for module in startUpExtensions:
	bot.load_extension(module)

getSettings("settings.json")
bot.run(botToken)

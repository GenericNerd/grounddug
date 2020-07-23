import discord
import asyncio
import jinja2

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape(["html", "htm"]),
    enable_async = True
)

async def purgeTemplate(title,messages):
    template = environment.get_template("purge.html")
    return discord.File(template.render_async(title=title,messages=messages),"file.html")
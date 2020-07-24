import discord
import asyncio
import jinja2
import os
from datetime import datetime

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape(["html", "htm"]),
    enable_async = True
)

async def purgeTemplate(title,messages):
    template = environment.get_template("purge.html")
    with open(f"{datetime.utcnow().strftime('%d%m%Y%H%M%S')}.html","w",encoding="UTF-8") as f:
        f.write(await template.render_async(title=title,messages=messages))
        f.close()
    return discord.File(f"{datetime.utcnow().strftime()}.html")
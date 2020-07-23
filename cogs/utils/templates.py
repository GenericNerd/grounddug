import discord
import asyncio
import jinja2
import io

environment = jinja2.Environment(
    loader=jinja2.FileSystemLoader("templates"),
    autoescape=jinja2.select_autoescape(["html", "htm"]),
    enable_async = True
)

async def purgeTemplate(title,messages):
    template = environment.get_template("purge.html")
    stream = io.StringIO()
    stream.write(await template.render_async(title=title,messages=messages))
    return discord.File(stream,"file.html")
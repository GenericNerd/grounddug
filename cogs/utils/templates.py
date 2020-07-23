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
    stream = io.BufferedIOBase()
    template = await template.render_async(title=title,messages=messages)
    stream.write(bytes(template,encoding="UTF-8"))
    return discord.File(stream,"file.html")
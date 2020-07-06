import asyncio
import socket

from sanic import Sanic
from sanic.response import json

app = Sanic(__name__)

@app.route('/')
async def webhook(request):
    pass

def registerVoteServer(loop, port=42069):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((socket.gethostname(), port))
    sock.listen(5)

    srv_coro = app.create_server(
        sock=sock,
        return_asyncio_server=True,
        asyncio_server_kwards=dict(
            start_serving=False
        )
    )

    srv = loop.run_until_complete(srv_coro)

    assert srv.is_serving() is False
    loop.run_until_complete(srv.start_serving())
    assert srv.is_serving() is True
    loop.create_task(srv.serve_forever)
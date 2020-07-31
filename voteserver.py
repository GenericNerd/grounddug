import asyncio
import socket
import cogs.utils.logger as logger
import cogs.utils.db as db

from sanic import Sanic
from sanic.response import json

app = Sanic(__name__)

@app.route('/')
async def webhook(request):
    return json({ 'message': 'GroundDug webhook server' })

@app.post('/topgg')
async def topgg(request):
    if 'Authorization' in request.headers:
        if request.headers['Authorization'] == 'f1jwhEi935knOndspVht':
            voteCount = 2 if request.json['isWeekend'] else 1
            userData = await db.getVoteUser(int(request.json['user']))
            if userData['linkedTo'] is not None:
                userData = await db.getVoteUser(userData['linkedTo'])
            userData['votes'] += voteCount
            await db.update('voteUsers', {'user': userData['user']}, userData)
            return json({ 'yay': True })
        else:
            return json({ 'yay': False })
    else:
        return json({ 'yay': False })

def registerVoteServer(loop, port=42069):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(5)

    srv_coro = app.create_server(
        sock=sock,
        return_asyncio_server=True,
        asyncio_server_kwargs=dict(
            start_serving=False
        )
    )

    srv = loop.run_until_complete(srv_coro)

    assert srv.is_serving() is False
    loop.run_until_complete(srv.start_serving())
    assert srv.is_serving() is True
    loop.create_task(srv.serve_forever())
    logger.success("Vote server registered")
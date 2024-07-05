import asynco
import websockets
import uuid
from datetime import datetime

connected_clients = {}
chat_history = []


async def file_server(websocket, path):
    
    # TODO: Implement the file server logic here
    try:
        await websocket.send("Welcome to the Shared File! Please enter your name:")
        username = await websocket.recv()

    except:
        pass

    finally:
        pass



start_server = websockets.serve(chat_server, 'localhost', 4444)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
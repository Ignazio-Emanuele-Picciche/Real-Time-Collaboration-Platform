import asynco
import websockets
import uuid
from datetime import datetime

connected_clients = {} # Dictionary to store the connected clients
chat_history = [] # List to store the chat history

async def send_to_all(message):
    """
    Broadcasts a message to all connected clients
    """
    # Loop through all connected clients and send the message
    if connected_clients:
        await asyncio.wait([client.send(message)] for client in connected_clients)


# async def send_chat_history(websocket):
#     """
#     Sends the entire chat history to the newly connected client
#     """
#     for message in chat_history:
#         await websocket.send(message)


async def send_user_list():
    """
    Broadcasts the list of currently connected users to all clients
    """
    # Loop through all connected clients and send the user list
    if connected_clients:
        user_list = "USERS: " + "," + ",".join(connected_clients.values())
        await asynco.wait([client.send(user_list_message)] for client in connected_clients)


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
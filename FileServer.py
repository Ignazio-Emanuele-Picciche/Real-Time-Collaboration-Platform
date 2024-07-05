import asyncio
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
        user_list_message = "USERS: " + "," + ",".join(connected_clients.values())
        await asyncio.wait([client.send(user_list_message)] for client in connected_clients)


'''
    In this method, we manage the principal logic of the file server:
    - It handles the connection and communication with clients
    - It maintains a list of connected clients and chat history
    - It menage disconnection of clients

    Args:
        websocket: The WebSocket connection object for a client
        path: The URL path requested by the client

    Returns:
        None
'''
async def file_server(websocket, path):

    try:
        await websocket.send("Welcome to the Shared File! Please enter your name:")
        username = await websocket.recv() # Wait for the client to send their username

        connected_clients[username] = websocket
        # await send_chat_history(websocket) # Send chat history to the new client
        join_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has joined the chat."
        await send_to_all(join_message) # Send a message to all connected clients
        chat_history.append(join_message) # Add the join_message to the chat history

        await send_user_list() # Update user list to all connected clients

        # Wait for messages from the client
        async for message in websocket:
            chat_message = f"{uuid.uuid4()}|{username}|{datetime.now().isoformat()}|{message}"
            chat_history.append(chat_message)
            await send_to_all(chat_message)
 
    except websockets.ConnectionClosed:
        pass

    finally:
        # Remove the client from the connected_clients dictionary
        leave_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has left the chat."
        connected_clients.pop(username)
        await send_to_all(leave_message) # Send a message to all connected clients that the user has left
        chat_history.append(leave_message)  

        await send_user_list()


# Start the server
start_server = websockets.serve(file_server, 'localhost', 4444) 

# Get the default event loop for the current context
asyncio.get_event_loop().run_until_complete(start_server)  # Start the server and run until the start_server coroutine is complete
asyncio.get_event_loop().run_forever()  # Run the event loop indefinitely to keep the server running
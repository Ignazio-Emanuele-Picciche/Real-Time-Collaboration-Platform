import asyncio
import uuid
import json
import os
from datetime import datetime
import websockets


connected_clients = {} # Dictionary to store the connected clients
chat_history = [] # List to store the chat history
FILE_PATH = "shared_file.txt" # Path to the shared file

async def send_to_all(message):
    """
    Broadcasts a message to all connected clients
    """
    # Loop through all connected clients and send the message
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])




# async def send_chat_history(websocket):
#      """
#      Sends the entire chat history to the newly connected client
#      """
#      for message in chat_history:
#          await websocket.send(message)


async def send_user_list():
    """
    Broadcasts the list of currently connected users to all clients
    """
    # Loop through all connected clients and send the user list
    if connected_clients:
        user_list_message = "USERS: " + "," + ",".join(connected_clients.values())
        await asyncio.wait([client.send(user_list_message) for client in connected_clients])

async def load_file():
    """
    Loads the contents of the shared file
    """
    if os.path.exists(FILE_PATH):
        with open (FILE_PATH, 'r') as file:
            return file.read()
    return ""

async def save_file(content):
    """
    Saves the contents of the shared file
    """
    with open (FILE_PATH, 'w') as file:
        file.write(content)

async def broadcast(message):
    """
    Broadcasts a message to all connected clients
    """
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])


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

        try:
            username = json.loads(username)
            
            if isinstance(username, dict):
                username = str(username['username']) 
            else:
                username = str(username)
                
        except json.JSONDecodeError:
            print('Error decoding JSON')

        connected_clients[websocket] = username
        # await send_chat_history(websocket) # Send chat history to the new client
        join_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has joined the document."
        await send_to_all(join_message) # Send a message to all connected clients
        # chat_history.append(join_message) # Add the join_message to the chat history

        await send_user_list() # Update user list to all connected clients
        content = await load_file() # Load the contents of the shared file
        await websocket.send(json.dumps({"type": "content", "content": content})) # Send the contents of the shared file to the client

        # Wait for messages from the client
        async for message in websocket:
            print('!!!!!HELPPP!!!!!')
            data = json.loads(message)
            if data['type'] == 'update':
                content = data['content']
                version = data['version']

                # print('\n'+str(version)+'\n')

                await save_file(content)
                await broadcast({"type": "content", "content": content, "version": version})

            # chat_message = f"{uuid.uuid4()}|{username}|{datetime.now().isoformat()}|{message}"
            # chat_history.append(chat_message)
            # await send_to_all(chat_message)
 
    except websockets.ConnectionClosed:
        pass

    finally:
        # Remove the client from the connected_clients dictionary
        leave_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has left the document."
        connected_clients.pop(websocket, None)
        await send_to_all(leave_message) # Send a message to all connected clients that the user has left
        # chat_history.append(leave_message)  

        await send_user_list()


# Start the server
start_server = websockets.serve(file_server, 'localhost',4000) 

# Get the default event loop for the current context
asyncio.get_event_loop().run_until_complete(start_server)  # Start the server and run until the start_server coroutine is complete
asyncio.get_event_loop().run_forever()  # Run the event loop indefinitely to keep the server running
import asyncio
import uuid
import json
import os
from datetime import datetime
import websockets


connected_clients = {} # Dictionary to store the connected clients
FILE_PATH = "shared_file.txt" # Path to the shared file

class CRDT:
    """
        This class implements the CRDT data structure for the shared file
    """
    def __init__(self):
        self.document = ""
        self.operations =[]
    
    # Method to generate a unique identifier for an operation
    def apply_operation(self, operation):
        if operation['type'] == 'insert':
            self.document = self.document[:operation['index']] + operation['char'] + self.document[operation['index']:]
        elif operation['type'] == 'delete':
            self.document = self.document[:operation['index']] + self.document[operation['index'] +1:]
            self.operations.append(operation)
    
    # Method to apply an operation to the document
    def get_document(self):
        return self.document

crdt = CRDT()

async def send_to_all(message):
    """
    Broadcasts a message to all connected clients
    """
    # Loop through all connected clients and send the message
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])

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
        join_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has joined the document."
        await send_to_all(join_message) # Send a message to all connected clients
        

        await send_user_list() # Update user list to all connected clients
        content = await load_file() # Load the contents of the shared file
        await websocket.send(json.dumps({"type": "content", "content": content})) # Send the contents of the shared file to the client

        # Wait for messages from the client
        async for message in websocket:
            data = json.loads(message)
            if data['type'] == 'update':
                content = data['content']
                version = data['version']
                operations = diff(crdt.get_document(), content)
                for op in operations:
                    crdt.apply_operation(op)
                await save_file(crdt.get_document())
                await broadcast({"type": "content", "content": crdt.get_document(), "version": version})
 
    except websockets.ConnectionClosed:
        pass

    finally:
        # Remove the client from the connected_clients dictionary
        leave_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has left the document."
        connected_clients.pop(websocket, None)
        await send_to_all(leave_message) # Send a message to all connected clients that the user has left
        await send_user_list()

'''
    This method calculates the difference between two strings and returns a list of operations to transform the old string into the new string
    
    Args:
        old_text: The old string
        new_text: The new string
    
    Returns:
        operations: A list of operations to transform the old string into the new string
'''
def diff(old_text, new_text):
    print('\nOld Text:', old_text)
    print('\nNew Text:', new_text)
    operations = []
    len_old, len_new = len(old_text), len(new_text)
    min_len = min(len_old, len_new)

    for i in range (min_len):
        if old_text[i] != new_text[i]:
            operations.append({'type': 'delete', 'index': i})
            operations.append({'type': 'insert', 'index': i, 'char': new_text[i]})
        
    if len_old > len_new:
        for i in range (min_len, len_old):
            operations.append({'type': 'delete', 'index': min_len})
    elif len_new > len_old:
        for i in range (min_len, len_new):
            operations.append({'type': 'insert', 'index': i, 'char': new_text[i]})
        
    return operations

# Start the server
start_server = websockets.serve(file_server, 'localhost',4000) 

# Get the default event loop for the current context
asyncio.get_event_loop().run_until_complete(start_server)  # Start the server and run until the start_server coroutine is complete
asyncio.get_event_loop().run_forever()  # Run the event loop indefinitely to keep the server running
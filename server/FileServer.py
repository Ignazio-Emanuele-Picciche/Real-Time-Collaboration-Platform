import asyncio
import uuid
import json
import os
from datetime import datetime
import websockets
from CRDT import CRDT
import difflib

connected_clients = {} # Dictionary to store the connected clients 
FILE_PATH = "shared_file.txt" # Path to the shared file
crdt = CRDT() # Create an instance of the CRDT class
start_server = ""


### MESSAGE MANAGEMENT FUNCTIONS ###
'''
    This method sends a message to all connected clients, such as when a user joins or leaves the document

    Args:
        message: The message to send to all clients

    Returns:
        None
'''
async def send_to_all(message):
    # Loop through all connected clients and send the message
    if connected_clients:
        await asyncio.wait([client.send(message) for client in connected_clients])


'''
    This message broadcasts a message to all connected clients, specifically designed to send file content updates to all clients. 
    This method uses JSON to serialize the messages, facilitating the transmission of structured data.

    Args:
        message: The document update message to broadcast
    
    Returns:
        None
'''
async def broadcast(message):
    if connected_clients:
        await asyncio.wait([client.send(json.dumps(message)) for client in connected_clients])


'''
    This method sends the list of currently connected users to all clients

    Args:
        None

    Returns:
        None
'''
async def send_user_list():
    # Loop through all connected clients and send the user list
    if connected_clients:
        user_list_message = "USERS: " + "," + ",".join(connected_clients.values())
        await asyncio.wait([client.send(user_list_message) for client in connected_clients])




### DOCUMENT MANAGEMENT FUNCTIONS ###
'''
    This method loads the contents of the shared file

    Args:
        None

    Returns:
        The contents of the shared file
'''
async def load_file():
    if os.path.exists(FILE_PATH):
        with open (FILE_PATH, 'r') as file:
            return file.read()
    return ""


'''
    Tjhis method saves the content in the shared file, updating the file with the new content

    Args:
        content: The content to save in the file

    Returns:
        None
'''
async def save_file(content):
    with open (FILE_PATH, 'w') as file:
        file.write(content)


'''
    This method calculates the difference between two strings and returns a new string that is consistent with both strings.
    This method uses the SequenceMatcher class from the difflib module to find differences and conflicts between the two strings.
    
    Args: 
        onlineText: The online text
        offlineText: The offline text
    
    Returns:
        A new string that is consistent with both strings
'''
def network_partition_consistency(onlineText, offlineText):
    # Use SequenceMatcher to find differences
    # SequenceMatcher is a class from the difflib module that helps to compare sequences of any type
    matcher = difflib.SequenceMatcher(None, onlineText, offlineText)
    result = []
    
    # Get and iterate through the operations (or "opcodes") that describe how to transform text1 into text2
    for opcode in matcher.get_opcodes():
        # Each opcode is a tuple containing: (tag, i1, i2, j1, j2)
        # tag: type of operation (equal, replace, delete, insert)
        # i1, i2: start and end index in onlineText
        # j1, j2: start and end index in offlineText
        tag, i1, i2, j1, j2 = opcode
        
        # If the parts are equal, add them to the result without changes
        if tag == 'equal':
            result.append(onlineText[i1:i2])
        # If there's a replacement, add both the text from onlineText and offlineText
        elif tag == 'replace':
            result.append(onlineText[i1:i2])
            result.append(offlineText[j1:j2])
        # If there's a deletion, add the text from onlineText
        elif tag == 'delete':
            result.append(onlineText[i1:i2])
        # If there's an insertion, add the text from offlineText
        elif tag == 'insert':
            result.append(offlineText[j1:j2])
        
    # Join all the pieces of text in the result and return it
    return ''.join(result)



### FILE SERVER LOGIC ###
'''
    In this method, are managed the principal operations of the file server:
    - It handles the connection and communication with clients
    - It maintains a list of connected clients and chat history
    - It menage disconnection of clients
    - It menage the CRDT operations
    - It menage the consistency of the document

    Args:
        websocket: The WebSocket connection object
        path: The path of the WebSocket connection

    Returns:
        None
'''
async def file_server(websocket, path):

    try:
        await websocket.send("Welcome to the Shared File! Please enter your name:")
        messageRecv = await websocket.recv() # Wait for the client to send their username
        type = ''
        username = ''

        try:
            messageRecv = json.loads(messageRecv)
            if isinstance(messageRecv, dict):
                username = str(messageRecv['username'])
                type = str(messageRecv['type']) 
            else:
                username = str(messageRecv)
        except json.JSONDecodeError:
            print('Error decoding JSON')

        connected_clients[websocket] = username # Add the client to the connected_clients dictionary
        join_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has joined the document."
        await send_to_all(join_message) # Send a message to all connected clients
        

        await send_user_list() # Update user list to all connected clients
        content = await load_file() # Load the contents of the shared file

        if type != 'reconnect':
            await websocket.send(json.dumps({"type": "content", "content": content})) # Send the contents of the shared file to the client
        else: # If the client is reconnecting, resolve the network partition, coflict and send the updated content
            content = messageRecv['content']
            updated_content = network_partition_consistency(crdt.get_document(), content)
            await save_file(updated_content)
            await broadcast({"type": "content", "content": updated_content})


        # Wait for messages from the client
        async for message in websocket:
            data = json.loads(message)

            if data['type'] == 'update':
                content = data['content']
                operations = crdt_operations(crdt.get_document(), content) # Calculate the operations to transform the old string into the new string, returning a list of operations

                for op in operations:
                    crdt.apply_operation(op)

                await save_file(crdt.get_document()) # Save the updated content to the shared file
                await broadcast({"type": "content", "content": crdt.get_document()}) # Broadcast the updated content to all connected clients
                
    except websockets.ConnectionClosed:
        print("Connection closed")

    finally:
        # Remove the client from the connected_clients dictionary
        leave_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has left the document."
        connected_clients.pop(websocket, None)
        await send_to_all(leave_message) # Send a message to all connected clients that the user has left
        await send_user_list()


### CRDT OPERATIONS ###
'''
    This method calculates the difference between two strings and returns a list of operations to transform the old string into the new string
    
    Args:
        old_text: The old string
        new_text: The new string
    
    Returns:
        operations: A list of operations to transform the old string into the new string
'''
def crdt_operations(old_text, new_text):
    operations = []
    len_old, len_new = len(old_text), len(new_text)
    min_len = min(len_old, len_new)

    # Iterate through the strings and find the differences till the minimum length,
    # adding the operations to the list, such as delete and insert
    for i in range (min_len):
        if old_text[i] != new_text[i]:
            operations.append({'type': 'delete', 'index': i})
            operations.append({'type': 'insert', 'index': i, 'char': new_text[i]})
    
    if len_old > len_new: # If the old string is longer than the new string, delete the remaining characters
        for i in range (min_len, len_old):
            operations.append({'type': 'delete', 'index': min_len})
    elif len_new > len_old: # If the new string is longer than the old string, add the remaining characters to the list
        for i in range (min_len, len_new):
            operations.append({'type': 'insert', 'index': i, 'char': new_text[i]})
        
    return operations




'''
    This method is the main method of the file server. It starts the WebSocket server on port 6000
'''
async def main():
    try:
        start_server = await websockets.serve(file_server, '0.0.0.0', 6000)
        print("WebSocket server started on ws://0.0.0.0:6000")
        await start_server.wait_closed()
    except Exception as e:
        print(f"Error starting server: {e}")
 
if __name__ == "__main__":
    asyncio.run(main())
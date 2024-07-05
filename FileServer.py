import asynco
import websockets
import uuid
from datetime import datetime

connected_clients = {}
chat_history = []


async def file_server(websocket, path):

    try:
        await websocket.send("Welcome to the Shared File! Please enter your name:")
        username = await websocket.recv()

        connected_clients[username] = websocket
        # await send_chat_history(websocket) # Send chat history to the new client
        join_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has joined the chat."
        await send_to_all(join_message)
        chat_history.append(join_message)

        await send_user_list()

        async for message in websocket:
            chat_message = f"{uuid.uuid4()}|{username}|{datetime.now().isoformat()}|{message}"
            chat_history.append(chat_message)
            await send_to_all(chat_message)
 
    except websockets.ConnectionClosed:
        pass

    finally:
        leave_message = f"{uuid.uuid4()}|System|{datetime.now().isoformat()}|{username} has left the chat."
        connected_clients.pop(username)
        await send_to_all(leave_message)
        chat_history.append(leave_message)  

        await send_user_list()


# Start the server
start_server = websockets.serve(chat_server, 'localhost', 4444) 

# Get the default event loop for the current context
asyncio.get_event_loop().run_until_complete(start_server)  # Start the server and run until the start_server coroutine is complete
asyncio.get_event_loop().run_forever()  # Run the event loop indefinitely to keep the server running
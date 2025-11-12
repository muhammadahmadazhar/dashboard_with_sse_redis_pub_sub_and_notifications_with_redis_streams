import asyncio

# Keep track of connected clients
clients = set()

async def event_stream():
    """Async generator for Server-Sent Events"""
    queue = asyncio.Queue()
    clients.add(queue)
    print(f"Client connected — total clients: {len(clients)}")
    try:
        while True:
            message = await queue.get()
            yield f"data: {message}\n\n"
    except asyncio.CancelledError:
        print("Client disconnected")
    finally:
        clients.remove(queue)

async def send_message(message: str):
    """Broadcast message to all connected clients"""
    print(f"Broadcasting to {len(clients)} clients: {message}")
    for q in clients:
        await q.put(message)

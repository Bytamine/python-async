import asyncio
import pickle

async def handle_conn(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"Client connected: {addr}")
    try:
        size_data = await reader.read(4)
        if len(size_data) < 4:
            raise ValueError("Incomplete size data received")
        size = int.from_bytes(size_data, 'big')
        request_data = await reader.read(size)
        if len(request_data) < size:
            raise ValueError("Incomplete request data received")
        request = pickle.loads(request_data)

        if request.get("type") == "greeting":
            response = {"message": "Hello World", "number": 42}
        else:
            response = {"error": "Unknown request type"}

        serialized_response = pickle.dumps(response)
        bsize = bytearray(4)
        bsize[:] = len(serialized_response).to_bytes(4, 'big')
        writer.write(bsize)
        writer.write(serialized_response)
        await writer.drain()
    except Exception as e:
        print(f"Error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()
        print(f"Client disconnected: {addr}")

async def main():
    try:
        server = await asyncio.start_server(handle_conn, "localhost", 8080)
        async with server:
            await server.serve_forever()
    except Exception as e:
        print(f"Server error: {e}")

asyncio.run(main())

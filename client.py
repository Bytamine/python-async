import asyncio
import pickle

async def recvall(reader, size):
    buf = bytearray()
    while len(buf) != size:
        chunk = await reader.read(size - len(buf))
        if len(chunk) == 0:
            raise Exception("disconnected")
        buf += chunk
    return buf

async def main():
    try:
        reader, writer = await asyncio.open_connection("localhost", 8080)

        request = {"type": "greeting"}
        serialized_request = pickle.dumps(request)
        bsize = bytearray(4)
        bsize[:] = len(serialized_request).to_bytes(4, 'big')
        writer.write(bsize)
        writer.write(serialized_request)
        await writer.drain()

        size_data = await recvall(reader, 4)
        if len(size_data) < 4:
            raise ValueError("Incomplete size data received")
        size = int.from_bytes(size_data, 'big')
        serialized_response = await recvall(reader, size)
        if len(serialized_response) < size:
            raise ValueError("Incomplete response data received")
        response = pickle.loads(serialized_response)
        print(response)
    except Exception as e:
        print(f"Client error: {e}")
    finally:
        writer.close()
        await writer.wait_closed()

asyncio.run(main())

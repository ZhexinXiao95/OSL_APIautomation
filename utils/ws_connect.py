import asyncio
import json

import websockets
import ssl

from utils.log import logger


class WebSocketClient:
    def __init__(self, uri):
        self.uri = uri
        self.connection = None

    async def connect(self):
        # 创建一个 SSLContext 对象，并设置为不验证证书
        ssl_context = ssl.create_default_context()
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_NONE

        self.connection = await websockets.connect(self.uri, ssl=ssl_context)
        print(f"Connected to {self.uri}")

    async def send_request(self, message):
        if self.connection is None:
            raise Exception("WebSocket is not connected. Call connect() first.")
        await self.connection.send(json.dumps(message))
        print(f"Sent: {message}")

    async def wait_for_response(self):
        if self.connection is None:
            raise Exception("WebSocket is not connected. Call connect() first.")
        response = await self.connection.recv()
        print(f"Received: {response}")
        return response

    async def close(self):
        if self.connection is not None:
            await self.connection.close()
            print("Connection closed")


# 示例使用：
async def websocket_connection(req, auth_token):
    logger.log(f'<===== connect websocket =====>')
    try:
        uri = f"wss://trade-hk-stage.oslsandbox.com/bcg/ws/ws-client?token={auth_token}"
        client = WebSocketClient(uri)
        await client.connect()
        await client.send_request(req)
        response = await client.wait_for_response()
        logger.log(f"Response from server: {response}")
        await client.close()
    except Exception as e:
        logger.log(f"An error occurred: {e}", 'error')
    finally:
        await client.close()
        logger.log('<===== disconnect websocket =====>')



# 运行客户端
if __name__ == "__main__":
    asyncio.run(websocket_connection())


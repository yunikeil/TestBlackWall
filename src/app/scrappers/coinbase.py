import websockets
import logging
import asyncio
import ujson

from core.settings import config
from core.utils.setup import setup_helper
from core.database.session import context_get_session
from core.redis.client import get_redis_client


logger = logging.getLogger("uvicorn")


class UsdtCourseWebScoket:
    def __init__(self):
        # TODO Получение пары usdt-usd для хранения в редисе, используется при конвертации перед записью в бд
        # https://docs.cdp.coinbase.com/advanced-trade/docs/ws-channels/#ticker-batch-channel
        self.ws_base_url = "wss://ws-feed.pro.coinbase.com"
        self.ticker_sub_msg = {
            "type": "subscribe",
            "channels": [{"name": "ticker_batch", "product_ids": ["USDT-USD"]}],
        }
    
    @staticmethod
    def get_helper_start():
        streamer = UsdtCourseWebScoket()
        return streamer.connect

    async def connect(self):
        logger.info(f'Coinbase listener USDT-USD started!')
        while True:
            try:
                async with websockets.connect(self.ws_base_url) as websocket:
                    await websocket.send(ujson.dumps(self.ticker_sub_msg))
                    await self.listen(websocket)
            except websockets.ConnectionClosedError:
                logger.warning("Connection closed by the server. Reconnecting...")
                await asyncio.sleep(5)
    
    async def handle_message(self, response_data: dict):
        # Не лучшее решение, можно было бы вынести в другое место, но ... одно число)
        async with get_redis_client() as redis:
           await redis.set("USDTUSD", response_data.get("price", '1'))
    
    async def listen(self, websocket: websockets.WebSocketClientProtocol):
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=30.0)
                response_data = ujson.loads(response)
                await self.handle_message(response_data)
            except asyncio.TimeoutError:
                logger.warning(
                    "No data received in the last 10 seconds. Reconnecting..."
                )
                await websocket.close()
                await self.connect()
                break
            except websockets.ConnectionClosedError as ex:
                if config.DEBUG:
                    logger.exception(ex)
                
                logger.warning("Connection closed by the server. Reconnecting...")
                await websocket.close()
                await self.connect()
                break


setup_helper.add_new_coroutine_def(UsdtCourseWebScoket.get_helper_start())

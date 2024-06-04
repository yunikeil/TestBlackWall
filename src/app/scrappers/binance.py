from typing import Literal
import websockets
import logging
import asyncio
import ujson
import uuid

from core.settings import config
from core.utils.setup import setup_helper
from core.database.session import context_get_session
from core.redis.client import get_redis_client
from app.schemas.binance import BookTickerStream, AveragePriceStream
from app.services.binance import (
    books_ticker_stream_service as tk_st_service,
    average_price_stream_service as avg_st_service,
)


logger = logging.getLogger("uvicorn")


class UsdtCourseWebScoket:
    def __init__(self):
        # Получение курса для хранения в редисе
        # Не хватило времени дописать, лоигка такова - мы пишем в редис соотношений usdt-usd
        # После при записи в базу данных мы сопоставляем данные курсы
        self.ws_base_url = "wss://ws-feed.pro.coinbase.com"
        self.ticker_sub_msg = {
            "type": "subscribe",
            "channels": [{"name": "ticker", "product_ids": ["USDT-USD"]}],
        }

        raise NotImplementedError

    ...


class RequestBinanceWebSocket:
    def __init__(self, method: Literal["ticker.price", "avgPrice"]) -> None:
        # Получение данных по запросу от клиента (от нас)
        # 1 секунда задержки ~500 (из 6000) запросов в минуту
        self.method = method
        self.symbols = ["BTCUSDT", "ETHUSDT"]
        self.ws_base_url = "wss://ws-api.binance.com:443/ws-api/v3"

    @staticmethod
    def get_helper_start(method: Literal["ticker.price", "avgPrice"]):
        streamer = RequestBinanceWebSocket(method)
        return streamer.connect

    async def connect(self):
        logger.info(f'BinanceRequest listener with "{self.method}" started!')
        while True:
            try:
                async with websockets.connect(self.ws_base_url) as websocket:
                    await self.communicate(websocket)
            except websockets.ConnectionClosedError:
                logger.warning("Connection closed by the server. Reconnecting...")
                await asyncio.sleep(5)

    async def process_symbol(
        self, symbol: str, websocket: websockets.WebSocketClientProtocol
    ):
        request = ujson.dumps(
            {
                "id": uuid.uuid4().hex,
                "method": self.method,
                "params": {"symbol": symbol},
            }
        )
        await websocket.send(request)
        response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
        return ujson.loads(response)

    async def communicate(self, websocket: websockets.WebSocketClientProtocol):
        while True:
            for symbol in self.symbols:
                try:
                    data = await self.process_symbol(symbol, websocket)
                    await self.handle_message(symbol, data["result"])
                except asyncio.TimeoutError:
                    logger.warning(
                        "No data received in the last 10 seconds. Reconnecting..."
                    )
                    await websocket.close()
                    await self.connect()
                    break
                except websockets.ConnectionClosedError as ex:
                    logger.exception(ex)
                    logger.warning("Connection closed by the server. Reconnecting...")
                    await websocket.close()
                    await self.connect()
                    break

            await asyncio.sleep(1)

    async def handle_message(self, symbol: str, response_data: dict):
        # print(symbol, self.method, response_data)
        ...

class StreamBinanceWebSocket:
    def __init__(self) -> None:
        # Получение БОЛЬШОГО количества данных через stream
        self.ws_base_url = "wss://stream.binance.com:9443/stream"
        self.ticker_param = "?streams=btcusdt@bookTicker/ethusdt@bookTicker"
        self.avg_param = "/btcusdt@avgPrice/ethusdt@avgPrice"

    @staticmethod
    def get_helper_start():
        streamer = StreamBinanceWebSocket()
        return streamer.connect

    async def connect(self):
        logger.info("Binance stream listener started!")
        ws_url = self.ws_base_url + self.ticker_param + self.avg_param
        while True:
            try:
                async with websockets.connect(
                    ws_url, ping_interval=None, ping_timeout=None, close_timeout=None
                ) as websocket:
                    await self.listen(websocket),
            except websockets.ConnectionClosedError:
                logger.warning("Connection closed by the server. Reconnecting...")
                await asyncio.sleep(5)

    async def handle_ticker(self, ticker: BookTickerStream):
        async with context_get_session() as db_session:
            await tk_st_service.create(db_session, ticker)

    async def handle_avg(self, avg: AveragePriceStream):
        async with context_get_session() as db_session:
            await avg_st_service.create(db_session, avg)

    async def handle_message(self, response_data: dict):
        if "bookTicker" in response_data["stream"]:
            ticker = BookTickerStream.model_validate(response_data["data"])
            await self.handle_ticker(ticker)
        elif "avgPrice" in response_data["stream"]:
            avg = AveragePriceStream.model_validate(response_data["data"])
            await self.handle_avg(avg)

    async def listen(self, websocket: websockets.WebSocketClientProtocol):
        while True:
            try:
                response = await asyncio.wait_for(websocket.recv(), timeout=10.0)
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
                logger.exception(ex)
                logger.warning("Connection closed by the server. Reconnecting...")
                await websocket.close()
                await self.connect()
                break


if config.NEED_STREAM_DATA:
    setup_helper.add_new_coroutine_def(StreamBinanceWebSocket.get_helper_start())

if config.NEED_REQUEST_DATA:
    ticker = RequestBinanceWebSocket.get_helper_start("ticker.price")
    average = RequestBinanceWebSocket.get_helper_start("avgPrice")
    setup_helper.add_new_coroutine_def(ticker)
    setup_helper.add_new_coroutine_def(average)

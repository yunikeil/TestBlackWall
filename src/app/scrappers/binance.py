import websockets
import logging
import asyncio
import ujson

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
            "channels": [
                {
                    "name": "ticker",
                    "product_ids": ["USDT-USD"]
                }
            ]
        }
        
        raise NotImplementedError
    
    ...
    


class ApiBinanceWebSocket:
    def __init__(self) -> None:
        # Получение данных по запросу от клиента (нас) 
        self.ws_base_url = "wss://ws-api.binance.com:443/ws-api/v3"
        
        raise NotImplementedError

    """Пример грязнового варианта
    
    class BinanceWebSocket:
        def __init__(self, symbol):
            self.symbol = symbol
            self.base_url = "wss://ws-api.binance.com:443/ws-api/v3"

        async def connect(self):
            async with websockets.connect(self.base_url) as websocket:
                await self.send_request(websocket)
                await self.listen(websocket)

        async def send_request(self, websocket):
            request_id = str(uuid.uuid4())
            request = {
                "id": request_id,
                "method": "ticker.price",
                "params": {
                    "symbol": self.symbol
                }
            }
            await websocket.send(json.dumps(request))

        async def listen(self, websocket):
            while True:
                response = await websocket.recv()
                data = json.loads(response)
                self.handle_message(data)

        def handle_message(self, message):
            print(message)

        def run(self):
            asyncio.get_event_loop().run_until_complete(self.connect())

    if __name__ == "__main__":
        symbol = "ETHUSDT"
        binance_ws = BinanceWebSocket(symbol)
        binance_ws.run()

    """

    ...


class StreamBinanceWebSocket:
    def __init__(self) -> None:
        # Получение БОЛЬШОГО количества данных через stream
        # С данным способом есть некоторые проблемы в виде отключения клиента от сервера
        # Когда то отключает через минут 5, когда то через 15
        #  попытался создать такое решение, но способ был описан на ноу нейм сайте, сомневаюсь в его работе
        #  (websocket.ping_callback = self.on_ping)
        # Если пинг не будет доходить, то на одном подключении код протянет 10 минут далее нужно будет переподключатсья (автоматически)
        
        self.ws_base_url = "wss://stream.binance.com:9443/stream"
        self.ticker_param = "?streams=btcusdt@bookTicker/ethusdt@bookTicker"
        self.avg_param = "/btcusdt@avgPrice/ethusdt@avgPrice"

    @staticmethod
    async def on_ping(websocket: websockets.WebSocketClientProtocol):
        logger.info("Received ping from server, sending pong...")
        await websocket.pong()

    async def connect(self):
        logger.info("Binance stream listener started!")
        ws_url = self.ws_base_url + self.ticker_param + self.avg_param
        while True:
            try:
                async with websockets.connect(
                    ws_url, ping_interval=None, ping_timeout=None, close_timeout=None
                ) as websocket:
                    websocket.ping_callback = self.on_ping
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


streamer = StreamBinanceWebSocket()
setup_helper.add_new_coroutine_def(streamer.connect)

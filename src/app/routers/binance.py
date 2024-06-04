from typing import Literal

from fastapi import Depends, Query, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.session import get_session
from app.services.binance import books_ticker_stream_service, average_price_stream_service


binance_router = APIRouter()


@binance_router.get("/getcurr/byticker", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    # Не совсем понял что именно в курсе трубется доставать
    """
    currency - курс валюты относительно usd <br>
    Для подсчёта к usd используйте поле `usdt_to_usd`
    """
    one_curr = await books_ticker_stream_service.get_one(db_session, currency)
    if not one_curr:
        raise HTTPException(404)
    
    return one_curr 

    
    
@binance_router.get("/getcurr/byaverage", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    # Не совсем понял что именно в курсе трубется доставать
    """
    currency - курс валюты относительно usd <br>
    Для подсчёта к usd используйте поле `usdt_to_usd`
    """
    one_curr = await average_price_stream_service.get_one(db_session, currency)
    if not one_curr:
        raise HTTPException(404)
    
    return one_curr 



@binance_router.get("/getcount/byticker", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    """
    currency - курс валюты относительно usd <br>
    Для подсчёта к usd используйте поле `usdt_to_usd`
    """
    count = await books_ticker_stream_service.count(db_session, currency)
    if not count:
        raise HTTPException(404)
    
    return {"count": count} 
    
    
@binance_router.get("/getcount/byaverage", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    """
    currency - курс валюты относительно usd <br>
    Для подсчёта к usd используйте поле `usdt_to_usd`
    """
    count = await average_price_stream_service.count(db_session, currency)
    if not count:
        raise HTTPException(404)
    
    return {"count": count}  



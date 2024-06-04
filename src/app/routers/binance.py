from typing import Literal

from fastapi import Depends, Query, APIRouter, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from core.database.session import get_session
from app.services.binance import books_ticker_stream_service, average_price_stream_service


binance_router = APIRouter()


@binance_router.get("/getcurr/ticker", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    # Не совсем понял что именно в курсе трубется доставать
    """
    currency - курс валюты относительно usd <br>
    """
    one_curr = await books_ticker_stream_service.get_one(db_session, currency)
    if not one_curr:
        raise HTTPException(404)
    
    return one_curr 

    
    
@binance_router.get("/getcurr/average", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    # Не совсем понял что именно в курсе трубется доставать
    """
    currency - курс валюты относительно usd <br>
    """
    one_curr = await average_price_stream_service.get_one(db_session, currency)
    if not one_curr:
        raise HTTPException(404)
    
    return one_curr 



@binance_router.get("/getcount/ticker", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    """
    currency - курс валюты относительно usd <br>
    """
    count = await books_ticker_stream_service.count(db_session, currency)
    if not count:
        raise HTTPException(404)
    
    return {"count": count} 
    
    
@binance_router.get("/getcount/average", tags=["data"])
async def get_binance_cource(
    currency: list[Literal["btcusdt", "ethusdt"]] = Query(["btcusdt", "ethusdt"]),
    db_session: AsyncSession = Depends(get_session)
):
    """
    currency - курс валюты относительно usd <br>
    """
    count = await average_price_stream_service.count(db_session, currency)
    if not count:
        raise HTTPException(404)
    
    return {"count": count}  



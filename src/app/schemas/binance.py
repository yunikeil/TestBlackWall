from datetime import datetime

from pydantic import BaseModel, Field


class BookTickerStream(BaseModel):
    update_id: int = Field(..., alias='u')
    symbol: str = Field(..., alias='s')
    best_bid: float = Field(..., alias='b')
    bid_qty: float = Field(..., alias='B')
    best_ask: float = Field(..., alias='a')
    asq_qty: float = Field(..., alias='A')


class BookTickerStreamDb(BookTickerStream):
    id: int
    created_at: datetime


class AveragePriceStream(BaseModel):
    event_type: str = Field(..., alias='e')
    event_time: int = Field(..., alias='E')
    symbol: str = Field(..., alias='s')
    interval: str = Field(..., alias='i')
    avg_price: float = Field(..., alias='w')
    last_trade_time: float = Field(..., alias='T')


class AveragePriceStreamDb(AveragePriceStream):
    id: int
    created_at: datetime

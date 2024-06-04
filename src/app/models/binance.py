from sqlalchemy import Column, BigInteger, VARCHAR, DECIMAL
from sqlalchemy.orm import relationship, Mapped

from core.database.base import Base


class BookTickerStreamModel(Base):
    __tablename__ = "book_ticker_stream"
    
    id = Column(BigInteger, primary_key=True)
    update_id = Column(BigInteger)
    symbol = Column(VARCHAR(10), index=True)
    best_bid = Column(DECIMAL(18,8)) # Цена
    bid_qty = Column(DECIMAL(18,8))
    best_ask = Column(DECIMAL(18,8))
    asq_qty = Column(DECIMAL(18,8))


class AveragePriceStreamModel(Base):
    __tablename__ = "average_price_stream"
    
    id = Column(BigInteger, primary_key=True)
    event_type = Column(VARCHAR(20))
    event_time = Column(BigInteger)
    symbol = Column(VARCHAR(10), index=True)
    interval = Column(VARCHAR(5))
    avg_price = Column(DECIMAL(18,8)) # Цена
    last_trade_time = Column(BigInteger)

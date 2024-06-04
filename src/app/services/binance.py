from typing import Literal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert, select, delete, func

from app.models.binance import BookTickerStreamModel, AveragePriceStreamModel
from app.schemas.binance import BookTickerStream, AveragePriceStream


class BookTickerStreamService:
    def __init__(self):
        pass

    async def create(self, db_session: AsyncSession, data: BookTickerStream):
        stmt = insert(BookTickerStreamModel).values(data.model_dump())
        await db_session.execute(stmt)
        await db_session.commit()

    async def get_one(self, db_session: AsyncSession, currency):
        stmt = (
            select(BookTickerStreamModel)
            .where(func.lower(BookTickerStreamModel.symbol).in_(currency))
            .limit(1)
        )
        query = await db_session.execute(stmt)
        return query.scalar_one_or_none()

    async def read(self, db_session: AsyncSession, id: int):
        stmt = select(BookTickerStreamModel).where(BookTickerStreamModel.id == id)
        result = await db_session.execute(stmt)
        return result.scalars().first()

    async def delete(self, db_session: AsyncSession, id: int):
        stmt = delete(BookTickerStreamModel).where(BookTickerStreamModel.id == id)
        await db_session.execute(stmt)
        await db_session.commit()

    async def count(
        self, db_session: AsyncSession, currency: list[Literal["btcusdt", "ethusdt"]]
    ):
        stmt = (
            select(func.count())
            .select_from(BookTickerStreamModel)
            .where(func.lower(BookTickerStreamModel.symbol).in_(currency))
        )
        result = await db_session.execute(stmt)
        return result.scalar()


class AveragePriceStreamService:
    def __init__(self):
        pass

    async def create(self, db_session: AsyncSession, data: AveragePriceStream):
        stmt = insert(AveragePriceStreamModel).values(data.model_dump())
        await db_session.execute(stmt)
        await db_session.commit()

    async def get_one(self, db_session: AsyncSession, currency):
        stmt = (
            select(AveragePriceStreamModel)
            .where(func.lower(AveragePriceStreamModel.symbol).in_(currency))
            .limit(1)
        )
        query = await db_session.execute(stmt)
        return query.scalar_one_or_none()

    async def read(self, db_session: AsyncSession, id: int):
        stmt = select(AveragePriceStreamModel).where(AveragePriceStreamModel.id == id)
        result = await db_session.execute(stmt)
        return result.scalars().first()

    async def delete(self, db_session: AsyncSession, id: int):
        stmt = delete(AveragePriceStreamModel).where(AveragePriceStreamModel.id == id)
        await db_session.execute(stmt)
        await db_session.commit()

    async def count(
        self, db_session: AsyncSession, currency: list[Literal["btcusdt", "ethusdt"]]
    ):
        stmt = (
            select(func.count())
            .select_from(AveragePriceStreamModel)
            .where(func.lower(AveragePriceStreamModel.symbol).in_(currency))
        )
        result = await db_session.execute(stmt)
        return result.scalar()


books_ticker_stream_service = BookTickerStreamService()
average_price_stream_service = AveragePriceStreamService()

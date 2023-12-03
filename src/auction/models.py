import datetime as dt
from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped
from sqlalchemy.types import ARRAY

import src.database as _db

import src.auction.utils as _auction_utils


class Lot(_db.Base):
    __tablename__ = 'lots'

    lot_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    title: Mapped[str] = mapped_column(sa.String(70))
    description: Mapped[str] = mapped_column(sa.String(750))
    creation_date: Mapped[dt.datetime] = mapped_column(default=_auction_utils.current_datetime)
    seller_id: Mapped[int] = mapped_column(sa.ForeignKey('users.user_id'))
    images: Mapped[Optional[list[str]]] = mapped_column(ARRAY(sa.String))
    base_price: Mapped[int]
    current_bid: Mapped[int]
    end_date: Mapped[dt.datetime]
    status: Mapped[str] = mapped_column(default='active')


class Bid(_db.Base):
    __tablename__ = 'bids'

    bid_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    lot_id: Mapped[int] = mapped_column(sa.ForeignKey('lots.lot_id'))
    bidder_id: Mapped[int] = mapped_column(sa.ForeignKey('users.user_id'))
    value: Mapped[int]
    placing_date: Mapped[dt.datetime] = mapped_column(default=_auction_utils.current_datetime)


class FavoriteLot(_db.Base):
    __tablename__ = 'favorite_lots'

    record_id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(sa.ForeignKey('users.user_id'))
    lot_id: Mapped[int] = mapped_column(sa.ForeignKey('lots.lot_id'))

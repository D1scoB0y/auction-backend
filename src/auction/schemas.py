import datetime as dt
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, field_validator
from fastapi import UploadFile, Form

import src.auction.validators as _auction_validators


class CreateLot(BaseModel):
    title: str
    description: str
    base_price: int
    end_date: dt.datetime
    images: list[UploadFile]

    @field_validator('images')
    def validate_images(cls, images: list[UploadFile]):
        return _auction_validators.validate_images(images)  # type: ignore

    @field_validator('end_date')
    def validate_end_date(cls, end_date: dt.datetime):
        return _auction_validators.validate_end_date(end_date)

    @field_validator('base_price')
    def validate_base_price(cls, base_price: int) -> int:
        if base_price < 0:
            raise ValueError('Base price must be greater than 0')

        return base_price

    @staticmethod
    def as_form(
        title: Annotated[str, Form(min_length=5, max_length=70)],
        base_price: Annotated[int, Form(alias='basePrice')],
        end_date: Annotated[dt.datetime, Form(alias='endDate')],
        images: list[UploadFile],
        description: Annotated[str, Form(max_length=500)] = '',
    ):
        return CreateLot(
            title=title,
            description=description,
            base_price=base_price,
            end_date=end_date,
            images=images,
        )


class ArchiveLot(BaseModel):
    lot_id: int = Field(alias='lotId')


class PreviewLot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lot_id: int = Field(alias='id')
    image: str
    title: str
    current_bid: int = Field(alias='currentBid')
    time_to_end: float = Field(alias='timeToEnd')
    status: str

    @staticmethod
    def from_lot(lot: dict):
        timedelta = lot['end_date'] - dt.datetime.utcnow()
        lot['time_to_end'] = timedelta.total_seconds()

        return PreviewLot(**lot)


class PreviewLotResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lots_qty: int = Field(alias='lotsQty')
    lots: list[PreviewLot]


class ReadLot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lot_id: int = Field(alias='lotId')
    title: str
    description: str
    base_price: int = Field(alias='basePrice')
    current_bid: int = Field(alias='currentBid')
    seller_id: int = Field(alias='sellerId')
    end_date: str = Field(alias='endDate')
    time_to_end: float = Field(alias='timeToEnd')
    images: list[str]

    @staticmethod
    def from_lot(lot: dict):
        timedelta = lot['end_date'] - dt.datetime.utcnow()
        lot['time_to_end'] = timedelta.total_seconds()
        lot['images'] = lot['images'][1:]
        lot['end_date'] = str(lot['end_date'])

        return ReadLot(**lot)


class PlaceBid(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lot_id: int = Field(alias='lotId')
    value: int


class ReadBid(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bidder_username: str = Field(alias='bidderUsername')
    value: int
    seconds_from_placing: int = Field(alias='secondsFromPlacing')

    @staticmethod
    def from_bid(bid: dict):
        timedelta = bid['placing_date'] - dt.datetime.utcnow()
        bid['seconds_from_placing'] = -int(timedelta.total_seconds())

        return ReadBid(**bid)


class ReadUserBids(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lot_id: int = Field(alias='lotId')
    max_user_bid_value: int = Field(alias='maxUserBidValue')
    lot_title: str = Field(alias='lotTitle')
    current_bid: int = Field(alias='currentBid')
    image: str
    lot_end_date: str = Field(alias='lotEndDate')
    time_to_end: int = Field(alias='timeToEnd')

    @staticmethod
    def from_bid(bid: dict):
        timedelta = bid['lot_end_date'] - dt.datetime.utcnow()

        bid['lot_end_date'] = str(bid['lot_end_date'])
        bid['time_to_end'] = int(timedelta.total_seconds())

        return ReadUserBids(**bid)


class UserBidsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bids_qty: int = Field(alias='bidsQty')
    bids: list[ReadUserBids]


class ReadEndedLot(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lot_id: int = Field(alias='lotId')
    title: str
    image: str
    end_date: str = Field(alias='endDate')
    ended_with_bids: bool = Field(alias='endedWithBids')

    @staticmethod
    def from_lot(lot: dict):
        lot['end_date'] = str(lot['end_date'])
        return ReadEndedLot(**lot)


class EndedLotsResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    lots_qty: int = Field(alias='lotsQty')
    lots: list[ReadEndedLot]


class ReadEndedLotBid(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    bidder_username: str = Field(alias='bidderUsername')
    bidder_email: str = Field(alias='bidderEmail')
    bidder_contacts: str | None = Field(alias='bidderContacts')
    value: int
    place: int

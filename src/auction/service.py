from sqlalchemy.ext.asyncio import AsyncSession

import src.user.models as _user_models
import src.auction.schemas as _auction_schemas
import src.auction.models as _auction_models
import src.auction.resizer_service as _resizer_service
import src.auction.yandex_cloud_service as _cloud_service
import src.auction.exception as _auction_exception
import src.auction.auction_getters as _auction_getters
import src.auction.utils as _auction_utils


async def create_lot(
    lot_data: _auction_schemas.CreateLot,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError('Only sellers can create lots.')

    new_lot = _auction_models.Lot(
        title=lot_data.title,
        description=lot_data.description,
        end_date=lot_data.end_date,
        seller_id=user.user_id,
        base_price=lot_data.base_price,
        current_bid=lot_data.base_price,
    )

    session.add(new_lot)
    await session.commit()
    await session.refresh(new_lot)

    resized_images = await _resizer_service.handle_images(lot_data.images)
    img_links = await _cloud_service.upload_images(new_lot.lot_id, resized_images)
    new_lot.images = img_links

    await session.commit()


async def archive_lot(
    lot_id: int,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError(
            'Only sellers can archive lots.',
        )

    orm_lot = await session.get(_auction_models.Lot, lot_id)

    if orm_lot is None:
        raise _auction_exception.LotNotFoundError(
            'Lot with such id does not exist',
        )

    orm_lot.status = 'archived'
    await session.commit()


async def fetch_lot(
    lot_id: int,
    session: AsyncSession,
):
    lot = await _auction_getters.get_lot_by_id(lot_id, session)

    if lot is None:
        raise _auction_exception.LotNotFoundError('Lot with this id does not exist.')

    return _auction_schemas.ReadLot.from_lot(lot)


async def fetch_active_lots(
    page: int,
    session: AsyncSession,
) -> _auction_schemas.PreviewLotResponse:
    lots = await _auction_getters.get_active_lots(session)

    lots_qty = await _auction_getters.get_active_lots_qty(session)

    limit = 15
    start = (page - 1) * limit
    end = page * limit

    lots_previews = list(map(
        lambda x: _auction_schemas.PreviewLot.from_lot(x),
        lots[start:end],
    ))

    res = _auction_schemas.PreviewLotResponse(**{'lots_qty': lots_qty, 'lots': lots_previews})

    return res


async def place_bid(
    bid_data: _auction_schemas.PlaceBid,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.email_is_verified:
        raise _auction_exception.MissingPermissionsError(
            'Only users with verified email can place bids.',
        )

    if not user.phone_number_is_verified:
        raise _auction_exception.MissingPermissionsError(
            'Only users with verified phone number can place bids.',
        )

    lot = await _auction_getters.get_lot_by_id(bid_data.lot_id, session)

    orm_lot = await session.get(_auction_models.Lot, bid_data.lot_id)

    if lot is None or orm_lot is None:
        raise _auction_exception.LotNotFoundError(
            'Lot not found.',
        )

    if not lot['status'] == 'active':
        raise _auction_exception.InactiveLotError(
            'Unable to place bid on inactive lot.',
        )

    if bid_data.value < _auction_utils.next_minimal_bid(lot['current_bid']):
        raise _auction_exception.BidValueError(
            'Bid is very low.',
        )

    orm_lot.current_bid = bid_data.value

    new_bid = _auction_models.Bid(
        lot_id=lot['lot_id'],
        bidder_id=user.user_id,
        value=bid_data.value,
    )

    session.add(new_bid)
    await session.commit()


async def fetch_lot_bids(
    lot_id: int,
    session: AsyncSession,
):
    bids = await _auction_getters.get_lot_bids(lot_id, session)

    res = list(map(
        _auction_schemas.ReadBid.from_bid,
        bids,
    ))

    return res


async def fetch_user_bids(
    page: int,
    user_id: int,
    session: AsyncSession,
):
    bids = await _auction_getters.get_user_bids(user_id, session)
    bids_qty = await _auction_getters.get_user_bids_qty(user_id, session)

    limit = 16
    start = (page - 1) * limit
    end = page * limit

    user_bids = list(map(
        _auction_schemas.ReadUserBids.from_bid,
        bids[start:end],
    ))

    res = _auction_schemas.UserBidsResponse(**{'bids_qty': bids_qty, 'bids': user_bids})

    return res


async def fetch_ended_lots(
    page,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError(
            'Only sellers can get ended lots',
        )

    lots = await _auction_getters.get_ended_lots(session)
    lots_qty = await _auction_getters.get_ended_lots_qty(session)

    limit = 15
    start = (page - 1) * limit
    end = page * limit

    ended_lots = list(map(
        _auction_schemas.ReadEndedLot.from_lot,
        lots[start:end],
    ))

    res = _auction_schemas.EndedLotsResponse(**{'lots': ended_lots, 'lots_qty': lots_qty})

    return res


async def fetch_ended_lot(
    lot_id: int,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError(
            'Only sellers can get ended lot with bids',
        )

    ended_lot = await _auction_getters.get_ended_lot(lot_id, session)

    if ended_lot is None:
        return None

    return _auction_schemas.ReadEndedLot.from_lot(ended_lot)


async def fetch_ended_lot_bids(
    lot_id: int,
    user: _user_models.User,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError(
            'Only sellers can get ended lot with bids',
        )

    ended_lot_bids = await _auction_getters.get_ended_lot_bids(lot_id, session)

    return list(map(
        lambda x: _auction_schemas.ReadEndedLotBid(**x),
        ended_lot_bids,
    ))


async def fetch_archived_lots(
    user: _user_models.User,
    page: int,
    session: AsyncSession,
):
    if not user.is_seller:
        raise _auction_exception.MissingPermissionsError(
            'Only sellers can get ended lot with bids',
        )

    lots = await _auction_getters.get_archived_lots(session)
    lots_qty = await _auction_getters.get_archived_lots_qty(session)

    limit = 15
    start = (page - 1) * limit
    end = page * limit

    lots_previews = list(map(
        lambda x: _auction_schemas.PreviewLot.from_lot(x),
        lots[start:end],
    ))

    res = _auction_schemas.PreviewLotResponse(**{'lots_qty': lots_qty, 'lots': lots_previews})

    return res

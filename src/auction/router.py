from fastapi import APIRouter, Depends, HTTPException, status

from sqlalchemy.ext.asyncio import AsyncSession

import src.database as _db
import src.utils as _utils
import src.user.models as _user_models
import src.auction.schemas as _auction_schemas
import src.auction.service as _auction_service
import src.user.utils as _user_utils
import src.auction.exception as _auction_exception


router = APIRouter(prefix='/auction')


@router.post(
    '/lots',
    status_code=status.HTTP_201_CREATED,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def create_lot(
    lot_data: _auction_schemas.CreateLot = Depends(
        _auction_schemas.CreateLot.as_form,
    ),
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _auction_service.create_lot(lot_data, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.patch(
    '/archive-lot',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def archive_lot(
    data: _auction_schemas.ArchiveLot,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _auction_service.archive_lot(data.lot_id, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except _auction_exception.LotNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    '/lots/{lot_id}',
    response_model=_auction_schemas.ReadLot,
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_lot(
    lot_id: int,
    user: _user_models.User = Depends(_user_utils.get_current_user_or_none),
    session: AsyncSession = Depends(_db.get_session)
):
    try:
        return await _auction_service.fetch_lot(lot_id, user, session)
    except _auction_exception.LotNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.post(
    '/add-to-favorites',
    status_code=status.HTTP_204_NO_CONTENT,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def add_to_favorites(
    data: _auction_schemas.AddToFavorites,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _auction_service.add_to_favorites(data.lot_id, user, session)
    except _auction_exception.LotNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )


@router.get(
    '/ended-lots/{lot_id}',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_ended_lot(
    lot_id: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        return await _auction_service.fetch_ended_lot(lot_id, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.get(
    '/active-lots',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_active_lots(
    page: int,
    user: _user_models.User = Depends(_user_utils.get_current_user_or_none),
    session: AsyncSession = Depends(_db.get_session),
):
    return await _auction_service.fetch_active_lots(page, user, session)


@router.get(
    '/favorite-lots',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_favorite_lots(
    page: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    return await _auction_service.fetch_favorite_lots(page, user, session)


@router.get(
    '/archived-lots',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_archived_lots(
    page: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    return await _auction_service.fetch_archived_lots(user, page, session)


@router.get(
    '/ended-lots',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_ended_lots(
    page: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        return await _auction_service.fetch_ended_lots(page, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )


@router.post(
    '/bids',
    status_code=status.HTTP_201_CREATED,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def place_bid(
    bid_data: _auction_schemas.PlaceBid,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        await _auction_service.place_bid(bid_data, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )
    except _auction_exception.LotNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except _auction_exception.InactiveLotError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=e.message,
        )
    except _auction_exception.BidValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=e.message,
        )


@router.get(
    '/lot-bids',
    response_model=list[_auction_schemas.ReadBid],
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_lot_bids(
    lot_id: int,
    session: AsyncSession = Depends(_db.get_session),
):
    return await _auction_service.fetch_lot_bids(lot_id, session)


@router.get(
    '/user-bids',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_user_bids(
    page: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    return await _auction_service.fetch_user_bids(page, user.user_id, session)


@router.get(
    '/ended-lot-bids/{lot_id}',
    status_code=status.HTTP_200_OK,
    tags=['Lots'],
)
@_utils.catch_unexpected_errors
async def get_ended_lot_bids(
    lot_id: int,
    user: _user_models.User = Depends(_user_utils.get_current_user),
    session: AsyncSession = Depends(_db.get_session),
):
    try:
        return await _auction_service.fetch_ended_lot_bids(lot_id, user, session)
    except _auction_exception.MissingPermissionsError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=e.message,
        )

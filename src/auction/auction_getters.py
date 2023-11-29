"""
    All functions will return json like {...} or [{...}, {...}]
"""
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text


async def get_lot_by_id(
    lot_id: int,
    session: AsyncSession,
) -> Optional[dict]:
    stmt = text('select * from lots where lot_id = :lot_id')
    lot = await session.execute(stmt, params={'lot_id': lot_id})
    lot = lot.first()

    if lot is None:
        return None

    return lot._asdict()


async def get_active_lots(
    session: AsyncSession,
) -> list[dict]:
    stmt = text('''
        select lot_id,
            title,
            end_date,
            current_bid,
            status,
            images[1] as image
        from lots
        where end_date > now() at time zone 'utc' and status = 'active'
    ''')

    lots = await session.execute(stmt)

    res = list(map(lambda x: x._asdict(), lots))

    return res


async def get_active_lots_qty(
    session: AsyncSession,
):
    stmt = text('''
        select count(*)
        from lots
        where end_date > now() at time zone 'utc' and status = 'active'
    ''')

    qty = await session.execute(stmt)

    return qty.scalar_one()


async def get_archived_lots(
    session: AsyncSession,
):
    stmt = text('''
        select lot_id,
            title,
            end_date,
            current_bid,
            status,
            images[1] as image
        from lots
        where status = 'archived'
    ''')

    lots = await session.execute(stmt)

    res = list(map(lambda x: x._asdict(), lots))

    return res


async def get_archived_lots_qty(
    session: AsyncSession,
):
    stmt = text('''
        select count(*)
        from lots
        where status = 'archived'
    ''')

    qty = await session.execute(stmt)

    return qty.scalar_one()


async def get_lot_bids(
    lot_id: int,
    session: AsyncSession,
) -> list[dict]:
    stmt = text('''
        select b.value,
            b.placing_date,
            u.username as bidder_username
        from bids b
        join users u on u.user_id = b.bidder_id
        where b.lot_id = :lot_id
    ''')

    bids = await session.execute(stmt, params={'lot_id': lot_id})

    res = list(map(lambda x: x._asdict(), bids))

    return res


async def get_ended_lots(
    session: AsyncSession,
) -> list[dict]:
    stmt = text('''
        select title,
            end_date,
            images[1] as image,
            lot_id,
            (current_bid > base_price) as ended_with_bids
        from lots
        where status = 'waiting_for_payment'
    ''')

    ended_lots = await session.execute(stmt)

    res = list(map(lambda x: x._asdict(), ended_lots))

    return res


async def get_ended_lots_qty(
    session: AsyncSession,
):
    stmt = text('''
        select count(*)
        from lots
        where status = 'waiting_for_payment'
    ''')

    qty = await session.execute(stmt)

    return qty.scalar_one()


async def get_user_bids(
    user_id: int,
    session: AsyncSession,
) -> list[dict]:
    stmt = text('''
        select b1.lot_id,
            b1.value as max_user_bid_value,
            l.title as lot_title,
            l.current_bid,
            l.images[1] as image,
            l.end_date as lot_end_date
        from bids b1
        join (
            select lot_id,
                max(value) as value
            from bids
            where bidder_id = :user_id
            group by lot_id
        ) as b2 on b2.lot_id = b1.lot_id and b2.value = b1.value
        join lots l on l.lot_id = b1.lot_id
        where l.status != 'archived'
    ''')

    bids = await session.execute(stmt, params={'user_id': user_id})

    res = list(map(lambda x: x._asdict(), bids))

    return res


async def get_user_bids_qty(
    user_id: int,
    session: AsyncSession,
):
    stmt = text('''
        select count(*)
        from bids b1
        join (
            select lot_id,
                max(value) as value
            from bids
            where bidder_id = :user_id
            group by lot_id
        ) as b2 on b2.lot_id = b1.lot_id and b2.value = b1.value
        join lots l on l.lot_id = b1.lot_id
        where l.status != 'archived'
    ''')

    qty = await session.execute(stmt, params={'user_id': user_id})

    return qty.scalar_one()


async def get_ended_lot(
    lot_id: int,
    session: AsyncSession,
) -> Optional[dict]:
    stmt = text('''
        select lot_id,
            title,
            images[1] as image,
            end_date,
            (current_bid > base_price) as ended_with_bids
        from lots
        where lot_id = :lot_id
    ''')

    ended_lot = await session.execute(stmt, params={'lot_id': lot_id})
    ended_lot = ended_lot.first()

    if ended_lot is None:
        return None

    return ended_lot._asdict()


async def get_ended_lot_bids(
    lot_id: int,
    session: AsyncSession,
) -> list[dict]:
    stmt = text('''
        select u.username as bidder_username,
            u.contacts as bidder_contacts,
            u.email as bidder_email,
            subquery.max_bid as value,
            row_number() over (order by subquery.max_bid desc) as place
        from (
            select bidder_id,
                max(value) as max_bid
            from bids
            where lot_id = :lot_id
            group by bidder_id
            order by max_bid desc
        ) as subquery
        join users u on u.user_id = subquery.bidder_id
    ''')

    ended_lot_bids = await session.execute(stmt, params={'lot_id': lot_id})

    return list(map(lambda x: x._asdict(), ended_lot_bids))

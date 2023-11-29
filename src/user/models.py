from typing import Optional

import sqlalchemy as sa
from sqlalchemy.orm import mapped_column, Mapped

import src.database as _db


class User(_db.Base):
    __tablename__ = 'users'

    user_id: Mapped[int] = mapped_column(primary_key=True, index=True)
    username: Mapped[str] = mapped_column(sa.String(16), unique=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    email_is_verified: Mapped[bool] = mapped_column(default=False)
    phone_number: Mapped[Optional[str]] = mapped_column(unique=True, index=True)
    phone_number_verif_code: Mapped[Optional[int]]
    phone_number_is_verified: Mapped[bool] = mapped_column(default=False)
    created_via_google: Mapped[bool] = mapped_column(default=False)
    password: Mapped[Optional[str]] = mapped_column(sa.String(64))
    is_seller: Mapped[bool] = mapped_column(default=False)
    contacts: Mapped[Optional[str]] = mapped_column(sa.String(200))

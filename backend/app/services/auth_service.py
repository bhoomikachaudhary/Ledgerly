from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.constants import DEFAULT_CATEGORIES
from app.core.security import (
    create_access_token,
    generate_refresh_token,
    hash_password,
    hash_refresh_token,
    verify_password,
)
from app.models.category import Category
from app.models.refresh_token import RefreshToken
from app.models.user import User
from app.schemas.auth import TokenPair, UserSignup


def signup(db: Session, data: UserSignup) -> User:
    existing = db.execute(select(User).where(User.email == data.email)).scalar_one_or_none()
    if existing is not None:
        raise HTTPException(status.HTTP_409_CONFLICT, "An account with this email already exists")

    user = User(
        email=data.email,
        password_hash=hash_password(data.password),
        name=data.name,
    )
    db.add(user)
    db.flush()  # assigns user.id without committing yet

    for defaults in DEFAULT_CATEGORIES:
        db.add(Category(user_id=user.id, **defaults))

    db.commit()
    db.refresh(user)
    return user


def authenticate(db: Session, email: str, password: str) -> User:
    user = db.execute(select(User).where(User.email == email)).scalar_one_or_none()
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid email or password")
    return user


def issue_token_pair(db: Session, user: User) -> TokenPair:
    """Create a fresh access token + refresh token, persisting the refresh token's hash."""
    access_token = create_access_token(user.id)
    raw_refresh, refresh_hash, expires_at = generate_refresh_token()

    db.add(RefreshToken(user_id=user.id, token_hash=refresh_hash, expires_at=expires_at))
    db.commit()

    return TokenPair(access_token=access_token, refresh_token=raw_refresh)


def rotate_refresh_token(db: Session, raw_refresh_token: str) -> TokenPair:
    """
    Validate an incoming refresh token, revoke it, and issue a brand new pair.
    Rotation means a stolen-then-reused refresh token is detected: it will already
    be revoked, so reuse fails closed.
    """
    token_hash = hash_refresh_token(raw_refresh_token)
    stored = db.execute(
        select(RefreshToken).where(RefreshToken.token_hash == token_hash)
    ).scalar_one_or_none()

    invalid = (
        stored is None
        or stored.revoked
        or stored.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc)
    )
    if invalid:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    stored.revoked = True

    user = db.get(User, stored.user_id)
    if user is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired refresh token")

    db.commit()
    return issue_token_pair(db, user)

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.schemas.auth import RefreshRequest, TokenPair, UserLogin, UserOut, UserSignup
from app.services import auth_service

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def signup(data: UserSignup, db: Session = Depends(get_db)) -> UserOut:
    user = auth_service.signup(db, data)
    return UserOut.model_validate(user)


@router.post("/login", response_model=TokenPair)
def login(data: UserLogin, db: Session = Depends(get_db)) -> TokenPair:
    user = auth_service.authenticate(db, data.email, data.password)
    return auth_service.issue_token_pair(db, user)


@router.post("/refresh", response_model=TokenPair)
def refresh(data: RefreshRequest, db: Session = Depends(get_db)) -> TokenPair:
    return auth_service.rotate_refresh_token(db, data.refresh_token)

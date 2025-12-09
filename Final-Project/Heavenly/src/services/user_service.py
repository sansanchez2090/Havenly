from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from models.enums import UserStatus

from models.user import User 
from schemas.user import UserCreate

bycrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService:
    @staticmethod
    def hash_password(password: str) -> str:
        return bycrypt_context.hash(password)


    @staticmethod
    def get_by_id(db: Session, user_id: int) -> Optional[User]:
        return db.query(User).filter(User.id == user_id).first()

    @staticmethod
    def get_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()

    @staticmethod
    def list_users(db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        return db.query(User).offset(skip).limit(limit).all()

    @staticmethod
    def create_user(db: Session, user_data: UserCreate) -> User:
        if UserService.get_by_email(db, user_data.email):
            raise ValueError("Email already registered")

        hashed = UserService.hash_password(user_data.password)

        db_user = User(
            first_name=user_data.first_name,
            last_name=user_data.last_name,
            email=user_data.email,
            area_code=user_data.area_code,
            phone_num=user_data.phone_num,
            photo_url=user_data.photo_url,
            status=UserStatus.VERIFIED,
            
            city_id=user_data.city_id,
            hash_password=hashed,
        )
        try:
            db.add(db_user)
            db.commit()
            db.refresh(db_user)
            return db_user
        except IntegrityError:
            db.rollback()
            raise

    @staticmethod
    def update_user(db: Session, user_id: int, payload) -> Optional[User]:
        user = UserService.get_by_id(db, user_id)
        if not user:
            return None

        data = payload.dict(exclude_unset=True) if hasattr(payload, "dict") else dict(payload)
        if "password" in data:
            user.hash_password = UserService.hash_password(data.pop("password"))

        for key, value in data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        try:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
        except Exception:
            db.rollback()
            raise



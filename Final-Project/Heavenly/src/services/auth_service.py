import os 
from datetime import datetime, timedelta, timezone
from typing import Annotated, Optional, List
from fastapi import Depends, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from passlib.context import CryptContext
from models.user import User
from schemas.user import UserCreate
from schemas.auth import Token
import jwt 
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from dotenv import load_dotenv 

load_dotenv()
oauth2_bearer =OAuth2PasswordBearer(tokenUrl='auth/tokens')
    

class AuthService:
    def __init__(self):
        self.bycrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.SECRET_KEY = os.getenv('SECRET_KEY')
        self.ALGORITHM = os.getenv('ALGORITHM')
        
    def hash_passwordse(self, password: str) -> str:
        return self.bycrypt_context.hash(password)


    def authenticate_user(self, email: str, password: str, db):
        user = db.query(User).filter(User.email == email).first()
        if not user:
            return False
        if not self.bycrypt_context.verify(password, user.hash_password):
            return False
        return user
        
    def create_access_token(self, email: str, user_id, expirate_delta: timedelta): 
        encode = {"sub": email, "id": user_id }
        expires = datetime.now(timezone.utc) + expirate_delta
        encode.update({"exp": expires})
        return jwt.encode(encode, self.SECRET_KEY, algorithm= self.ALGORITHM)
        
    async def get_current_user(self, token: Annotated[str, Depends(oauth2_bearer)]):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALGORITHM])
            email: str = payload.get('sub')
            user_id: int = payload.get('id')
            user_role: str = payload.get('role')
            if email is None or user_id is None: 
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                    detail='Could not validate user.')
                return {'email': email, 'id': user_id }
        except InvalidTokenError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
            
    
    @staticmethod
    def authenticate(
              db: Session, 
              form_data) -> Token:
        auth = AuthService()
        user = auth.authenticate_user(form_data.username, form_data.password, db)
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user. ')
            HTTPException()

        token = auth.create_access_token(user.email, user.id,timedelta(minutes=20))
        return Token(access_token=token, token_type='bearer')

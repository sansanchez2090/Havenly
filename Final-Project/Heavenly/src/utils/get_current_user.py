from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer
import jwt 
from jwt.exceptions import PyJWTError

security = HTTPBearer()

def get_current_user(credentials = Depends(security)) -> dict:
    token = credentials.credentials
    
    try:
        # 1. Decodificar token con tu clave secreta
        payload = jwt.decode(token, "SECRET_KEY", algorithms=["HS256"])
        
        # 2. Extraer datos del usuario del payload
        user_id = payload.get("sub")  # o el campo que uses
        
        # 3. Retornar diccionario con datos usuario
        return {"id": user_id, "email": payload.get("email")}
    
    except PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
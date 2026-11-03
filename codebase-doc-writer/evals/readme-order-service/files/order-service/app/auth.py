import jwt
from fastapi import Header, HTTPException

from app.config import settings


def get_current_user(authorization: str = Header(...)) -> str:
    """Trả về user_id từ JWT HS256 trong header Authorization: Bearer <token>."""
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Missing bearer token")
    try:
        payload = jwt.decode(authorization[7:], settings.jwt_secret, algorithms=["HS256"])
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    return str(payload["sub"])

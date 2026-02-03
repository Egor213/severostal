from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer

from src.utils.jwt import TokenExpire, decode_token

security = HTTPBearer(auto_error=False)

import os


def get_current_user(authorization: HTTPBearer | None = Depends(security)) -> dict:
    # if os.getenv("TEST"):
    #     return {"id": 10, "exp": 1772724243}

    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = authorization.credentials

    try:
        user_data = decode_token(token)
        return user_data
    except TokenExpire:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expired",
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )

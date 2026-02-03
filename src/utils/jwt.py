from datetime import datetime, timedelta, timezone

from jose import jwt

from src.config import get_auth_data


class TokenExpire(Exception):
    @property
    def message(self):
        return "Token is expire"


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    auth_data = get_auth_data()
    expire = datetime.now(timezone.utc) + timedelta(days=auth_data["time_expire"])
    to_encode.update({"exp": expire})
    encode_jwt = jwt.encode(to_encode, auth_data["secret_key"], algorithm=auth_data["algorithm"])
    return encode_jwt


def decode_token(token: str):
    auth_data = get_auth_data()
    payload = jwt.decode(token, auth_data["secret_key"], algorithms=auth_data["algorithm"])

    exp = payload.get("exp")
    if exp and datetime.now(timezone.utc) > datetime.fromtimestamp(exp):
        raise TokenExpire

    return payload

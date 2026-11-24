import os
import hmac
import hashlib
import json
import base64
import time
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from app.config import settings

def _b64encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b'=').decode('ascii')

def _b64decode(data: str) -> bytes:
    padding = 4 - (len(data) % 4)
    if padding != 4:
        data += '=' * padding
    return base64.urlsafe_b64decode(data.encode('ascii'))

def hash_password(password: str) -> str:
    try:
        import bcrypt
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(pwd_bytes, salt).decode('utf-8')
    except ImportError:
        # Standard library PBKDF2-HMAC-SHA256
        salt = os.urandom(16)
        key = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, 100000)
        return f"pbkdf2${salt.hex()}${key.hex()}"

def verify_password(plain_password: str, hashed_password: str) -> bool:
    if hashed_password.startswith("pbkdf2$"):
        try:
            _, salt_hex, key_hex = hashed_password.split("$")
            salt = bytes.fromhex(salt_hex)
            expected_key = bytes.fromhex(key_hex)
            key = hashlib.pbkdf2_hmac('sha256', plain_password.encode('utf-8'), salt, 100000)
            return hmac.compare_digest(key, expected_key)
        except Exception:
            return False
    else:
        try:
            import bcrypt
            return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
        except Exception:
            return False

def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
    try:
        from jose import jwt
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.access_token_expire_minutes))
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    except ImportError:
        # Pure Python RFC 7519 HS256 JWT
        header = {"alg": "HS256", "typ": "JWT"}
        payload = data.copy()
        now_ts = int(time.time())
        exp_ts = now_ts + int((expires_delta.total_seconds() if expires_delta else settings.access_token_expire_minutes * 60))
        payload["iat"] = now_ts
        payload["exp"] = exp_ts

        header_b64 = _b64encode(json.dumps(header, separators=(',', ':')).encode('utf-8'))
        payload_b64 = _b64encode(json.dumps(payload, separators=(',', ':')).encode('utf-8'))
        signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
        signature = hmac.new(settings.secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
        sig_b64 = _b64encode(signature)
        return f"{header_b64}.{payload_b64}.{sig_b64}"

def decode_access_token(token: str) -> Optional[Dict[str, Any]]:
    try:
        from jose import jwt, JWTError
        return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except ImportError:
        # Pure Python HS256 verification
        try:
            parts = token.split('.')
            if len(parts) != 3:
                return None
            header_b64, payload_b64, sig_b64 = parts
            signing_input = f"{header_b64}.{payload_b64}".encode('ascii')
            expected_sig = hmac.new(settings.secret_key.encode('utf-8'), signing_input, hashlib.sha256).digest()
            actual_sig = _b64decode(sig_b64)
            if not hmac.compare_digest(expected_sig, actual_sig):
                return None
            payload = json.loads(_b64decode(payload_b64).decode('utf-8'))
            if "exp" in payload and payload["exp"] < time.time():
                return None
            return payload
        except Exception:
            return None
    except Exception:
        return None

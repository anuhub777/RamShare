import hashlib

def generate_idempotency_key(*parts: str) -> str:
    raw = ":".join(str(p) for p in parts)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

# Obfuscation utility for IDs
import os
from typing import Optional
from hashlib import blake2b
import base64

OBFUSCATION_KEY = os.getenv("ID_OBFUSCATION_KEY", "default_key")

# You can override the key for testing or other services

def obfuscate_id(id_int: int, key: Optional[str] = None) -> str:
    key = (key or OBFUSCATION_KEY).encode()
    h = blake2b(digest_size=6, key=key)
    h.update(str(id_int).encode())
    digest = h.digest() + id_int.to_bytes(6, 'big')
    return base64.urlsafe_b64encode(digest).decode().rstrip('=')

def deobfuscate_id(obf_id: str, key: Optional[str] = None) -> int:
    key = (key or OBFUSCATION_KEY).encode()
    padded = obf_id + '=' * (-len(obf_id) % 4)
    raw = base64.urlsafe_b64decode(padded)
    digest, id_bytes = raw[:6], raw[6:]
    id_int = int.from_bytes(id_bytes, 'big')
    h = blake2b(digest_size=6, key=key)
    h.update(str(id_int).encode())
    if h.digest() != digest:
        raise ValueError("Invalid obfuscated ID or key")
    return id_int

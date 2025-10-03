import os
import base64
from hmtracker.common.constants import HM_SECRET_KEY_ENV_NAME
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC


def _get_fernet_key() -> Fernet:
    """Get or derive Fernet encryption key from environment variable."""
    secret_key = os.getenv(HM_SECRET_KEY_ENV_NAME)
    if not secret_key:
        raise ValueError(f"{HM_SECRET_KEY_ENV_NAME} environment variable not set")

    # Derive a consistent key from the secret
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=b"hockey_manager_salt",  # Fixed salt for consistency
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(secret_key.encode()))
    return Fernet(key)


def encrypt(value: str) -> str:
    """Encrypt a string value using Fernet symmetric encryption."""
    if not value:
        return ""

    fernet = _get_fernet_key()
    encrypted_bytes = fernet.encrypt(value.encode("utf-8"))
    return base64.urlsafe_b64encode(encrypted_bytes).decode("utf-8")


def decrypt(value: str) -> str:
    """Decrypt a string value using Fernet symmetric encryption."""
    if not value:
        return ""

    try:
        fernet = _get_fernet_key()
        encrypted_bytes = base64.urlsafe_b64decode(value.encode("utf-8"))
        decrypted_bytes = fernet.decrypt(encrypted_bytes)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Decryption failed: {str(e)}")

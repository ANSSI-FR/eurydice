import logging
from pathlib import Path

from django.conf import settings
from nacl.public import PrivateKey

logger = logging.getLogger(__name__)


class Keypair:
    _instance = None

    def __new__(cls, *args, **kwargs) -> "Keypair":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.verify_keys_exist()
            cls._instance._init_asymmetrical_keys()
        return cls._instance

    def verify_keys_exist(self) -> None:
        """
        Verifies if a keypair is already generated
        Raises:
            MissingPrivateKey: When one of the key file is missing.
        """
        if not Path(settings.PRIVKEY_PATH).is_file():
            raise MissingPrivateKey("Missing Private key. Verify that the path to the key is correct.")

    def _init_asymmetrical_keys(self) -> None:
        privkey_path = Path(settings.PRIVKEY_PATH)

        self.private_key = privkey_path.read_bytes()
        self.public_key = PrivateKey(self.private_key).public_key.encode()

        invalid_keys = []
        if len(self.public_key) != 32:
            invalid_keys.append("Public key")
        if len(self.private_key) != 32:
            invalid_keys.append("Private key")

        if invalid_keys:
            raise InvalidKey(f"{', '.join(invalid_keys)} with invalid length (!=32)")


class InvalidKey(RuntimeError):
    """Whenever a symmetric or asymmetric key is wrong"""

    pass


class MissingPrivateKey(RuntimeError):
    """
    Whenever the private key is
    missing when trying to decrypt a file
    """

    pass

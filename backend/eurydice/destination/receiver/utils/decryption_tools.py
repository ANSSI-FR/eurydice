import logging

import nacl.bindings

from eurydice.destination.core.models.incoming_transferable import (  # noqa: E501
    IncomingTransferable,
)
from eurydice.destination.receiver.utils.keypair import Keypair

logger = logging.getLogger(__name__)


class DecryptionTools:
    """Stores all data and function to decrypt incoming transferables"""

    def __init__(self, incoming_transferable: IncomingTransferable):
        self.keypair = Keypair()

        self._init_metadata(incoming_transferable)
        self.symmetric_key = self._decrypt_symmetric_key()
        self.init_decryption()

    def init_decryption(self) -> None:
        """Initiate the state of the decryption process
        The state increments at each decryption
        It uses the header used to encrypt the data to decrypt the
        same data in the same order
        """
        self.state = nacl.bindings.crypto_secretstream_xchacha20poly1305_state()
        nacl.bindings.crypto_secretstream_xchacha20poly1305_init_pull(self.state, self.header, self.symmetric_key)

    def decrypt_chunk(self, encrypted_chunk: bytes) -> bytes:
        """Decrypts a chunk of data from a transferable"""
        decrypted_chunk, _ = nacl.bindings.crypto_secretstream_xchacha20poly1305_pull(self.state, encrypted_chunk)
        return decrypted_chunk

    def _init_metadata(self, incoming_transferable: IncomingTransferable) -> None:
        self.nb_chunks = int(incoming_transferable.user_provided_meta["Metadata-Parts-Count"])
        self.chunk_size = int(incoming_transferable.user_provided_meta["Metadata-Main-Part-Size"])
        self.last_chunk_size = int(incoming_transferable.user_provided_meta["Metadata-Last-Part-Size"])
        self.header = self._metadata_to_bytes_list(incoming_transferable.user_provided_meta["Metadata-Header"])
        self.encrypted_symmetric_key = self._metadata_to_bytes_list(
            incoming_transferable.user_provided_meta["Metadata-Encrypted-Symmetric-Key"]
        )

    def _metadata_to_bytes_list(self, metadata_str: str) -> bytes:
        """Metadata are received as strings
        This converts javascript byte arrays (Uint8Array) into python bytes"""
        meta_byte_list = [int(num) for num in metadata_str.split(",")]
        return bytes(meta_byte_list)

    def _decrypt_symmetric_key(self) -> bytes:
        """Symmetric key is received with the Transferable
        It is encrypted with the public key"""
        if len(self.encrypted_symmetric_key) < 48:
            raise InvalidKey("Encrypted Symmetrical key has invalid length (<48)")
        return nacl.bindings.crypto_box_seal_open(
            self.encrypted_symmetric_key, self.keypair.public_key, self.keypair.private_key
        )


class InvalidKey(RuntimeError):
    """Whenever a symmetric or asymmetric key is wrong"""

    pass

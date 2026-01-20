import pytest
from nacl.exceptions import CryptoError

from eurydice.destination.core.models.incoming_transferable import IncomingTransferable
from eurydice.destination.receiver.utils.decryption_tools import DecryptionTools, InvalidKey
from tests.common.decryption_constants import (
    ENCRYPTED_PART,
    EXPECTED_HEADER,
    EXPECTED_PART,
    EXPECTED_SYMKEY,
    PRIVKEY,
    PUBKEY,
    user_provided_metadata_encrypted,
)


class TestDecryption:
    def test_decryption_should_succeed(self):
        dummy_transferable = self._init_transferable()
        decryption_tools = DecryptionTools(dummy_transferable)
        decryption_tools.public_key = PUBKEY
        decryption_tools.private_key = PRIVKEY
        assert decryption_tools.symmetric_key == EXPECTED_SYMKEY
        assert decryption_tools.header == EXPECTED_HEADER

        decrypted_chunk = decryption_tools.decrypt_chunk(ENCRYPTED_PART)
        assert decrypted_chunk == EXPECTED_PART

    def test_missing_metadata_should_fail(self):
        dummy_transferable = self._init_transferable()
        dummy_transferable.user_provided_meta.pop("Metadata-Parts-Count")
        with pytest.raises(KeyError, match="Metadata-Parts-Count"):
            decryption_tools = DecryptionTools(dummy_transferable)
            assert decryption_tools.symmetric_key != EXPECTED_SYMKEY

    def test_incorrect_secret_key_should_fail(self):
        dummy_transferable = self._init_transferable()
        dummy_transferable.user_provided_meta["Metadata-Encrypted-Symmetric-Key"] = (
            "1,245,66,128,236,26,58,47"
            ",47,112,251,237,250,22,194,128,51,247,231,193,1,149,213,25"
            ",221,95,214,215,77,237,48,33,103,220,52,246,189,210,113,23"
            "7,106,145,11,90,67,193,207,210,36,73,185,205,219,195,249,2"
            "14,89,21,165,199,86,221,51,175,69,154,204,190,246,71,85,20"
            "4,245,142,31,163,145,150,71,96"
        )
        with pytest.raises(CryptoError, match="error occurred trying to decrypt the message"):
            decryption_tools = DecryptionTools(dummy_transferable)
            assert decryption_tools.symmetric_key != EXPECTED_SYMKEY
        dummy_transferable.user_provided_meta["Metadata-Encrypted-Symmetric-Key"] = (
            "190,246,71,85,204,245,142,31,163,145,150,71,96"
        )
        with pytest.raises(InvalidKey, match="key has invalid length"):
            decryption_tools = DecryptionTools(dummy_transferable)
            assert decryption_tools.symmetric_key != EXPECTED_SYMKEY

    def _init_transferable(self) -> IncomingTransferable:
        return IncomingTransferable(
            name="test.txt",
            user_provided_meta=user_provided_metadata_encrypted.copy(),
        )

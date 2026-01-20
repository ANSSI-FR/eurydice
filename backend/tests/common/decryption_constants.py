# Using dummy data that work together
# These can be found using console.log() inside the frontend,
# when using libsodium to encrypt the chunks.
# All values are interconnected, changing one should break the encryption/decryption
PUBKEY = b"\x82\xd0\xb7\xd8\xb1\xf5\x9f\xaa\x82nJ\x90\xa2\x0f\xd0\xc0\n\xfbN<n\x10=\xbe\xf3\x9a5\t\x19R\x97f"  # noqa: E501
PRIVKEY = b"\x1b.\xe9\x14W\xf8\x9f'\x07\x81\xaa\xc6C\xec\x92K\xaa\x89\xf9\x04:\x016\xa4\x97\x84\xd6\xe3\xe8\xaa)\xd7"  # noqa: E501
EXPECTED_HEADER = b'\x0e\xb3\x83\xb3\x85")X_\x03\x07\x14\x01\xe5\xda\xdf\n\x1b\xc9I)\xc9\x98\xfd'
ENCRYPTED_SYMKEY = b"O\xf5B\x80\xec\x1a://p\xfb\xed\xfa\x16\xc2\x803\xf7\xe7\xc1\x01\x95\xd5\x19\xdd_\xd6\xd7M\xed0!g\xdc4\xf6\xbd\xd2q\xedj\x91\x0bZC\xc1\xcf\xd2$I\xb9\xcd\xdb\xc3\xf9\xd6Y\x15\xa5\xc7V\xdd3\xafE\x9a\xcc\xbe\xf6GU\xcc\xf5\x8e\x1f\xa3\x91\x96G`"  # noqa: E501
EXPECTED_SYMKEY = b"\xa9e\x19\xff\x18\x1c[_\x875\n\xb4k\xe6\xc9\xebwOKAl\x00\xd7\xcf\x92*\xbd\xf8\x1c\xb8\x973"  # noqa: E501
ENCRYPTED_PART = b"h\xb7\xcf\xde\xe6dJ||\xd1\x9b\x8c\xfc\xd3'`\xcf\xe2\xcb\xf3\x04"
EXPECTED_PART = b"test"

user_provided_metadata_encrypted = {
    "Metadata-Encrypted-Size": "21",
    "Metadata-Encrypted": "true",
    "Metadata-Parts-Count": "1",
    "Metadata-Main-Part-Size": "21",
    "Metadata-Last-Part-Size": "21",
    "Metadata-Encrypted-Symmetric-Key": (
        "79,245,66,128,236,26,58,47"
        ",47,112,251,237,250,22,194,128,51,247,231,193,1,149,213,25"
        ",221,95,214,215,77,237,48,33,103,220,52,246,189,210,113,23"
        "7,106,145,11,90,67,193,207,210,36,73,185,205,219,195,249,2"
        "14,89,21,165,199,86,221,51,175,69,154,204,190,246,71,85,20"
        "4,245,142,31,163,145,150,71,96"
    ),
    "Metadata-Header": ("14,179,131,179,133,34,41,88,95,3,7,20,1,229,218,223,10,27,201,73,41,201,152,253"),
}

__all__ = (
    "user_provided_metadata_encrypted",
    "PUBKEY",
    "PRIVKEY",
    "EXPECTED_HEADER",
    "ENCRYPTED_SYMKEY",
    "EXPECTED_SYMKEY",
    "ENCRYPTED_PART",
    "EXPECTED_PART",
)

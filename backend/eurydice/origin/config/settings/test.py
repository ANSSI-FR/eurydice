import os

os.environ.setdefault("LIDIS_HOST", "127.0.0.1")
os.environ.setdefault("LIDIS_PORT", "1")

from eurydice.origin.config.settings.base import *  # noqa

from eurydice.common.config.settings.test import *

os.environ["TRANSFERABLE_STORAGE_DIR"] = "/tmp/eurydice-data/origin"  # nosec
ENCRYPTION_ENABLED = False
PUBKEY_PATH = "/home/eurydice/keys/eurydice.pub"

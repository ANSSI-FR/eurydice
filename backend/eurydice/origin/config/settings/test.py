import os

os.environ.setdefault("LIDIS_HOST", "127.0.0.1")
os.environ.setdefault("LIDIS_PORT", "1")

from eurydice.origin.config.settings.base import *

from eurydice.common.config.settings.test import *  # isort:skip

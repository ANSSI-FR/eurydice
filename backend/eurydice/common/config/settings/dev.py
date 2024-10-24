from eurydice.common.config.settings.base import *

DEBUG = True

env = environ.Env(
    FAKER_SEED=(int, 9835234),
)

FAKER_SEED = env("FAKER_SEED")

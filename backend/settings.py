"""
Dynamically generated Django settings.
Workaround to use django-stubs with multiple django projects.
"""

import importlib
import os

# Import the module
mod = importlib.import_module(os.environ["DS"])

# Determine a list of names to copy to the current name space
names = getattr(mod, "__all__", [n for n in dir(mod) if not n.startswith("_")])

# Copy those names into the current name space
g = globals()
for name in names:
    g[name] = getattr(mod, name)

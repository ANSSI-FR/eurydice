#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    DJANGO_ENV = os.environ.get("DJANGO_ENV", None)
    EURYDICE_API = os.environ.get("EURYDICE_API", "origin")
    if DJANGO_ENV is None:
        settings_module = "base"
    else:
        settings_module = DJANGO_ENV.lower()

    DJANGO_SETTINGS_MODULE = (
        f"eurydice.{EURYDICE_API}.config.settings.{settings_module}"
    )

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", DJANGO_SETTINGS_MODULE)

    print(f"Using '{DJANGO_SETTINGS_MODULE}' as DJANGO_SETTINGS_MODULE")

    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)

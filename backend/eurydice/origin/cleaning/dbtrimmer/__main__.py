if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eurydice.origin.config.settings.base")
    django.setup()

    from eurydice.origin.cleaning.dbtrimmer import dbtrimmer

    dbtrimmer.OriginDBTrimmer().start()

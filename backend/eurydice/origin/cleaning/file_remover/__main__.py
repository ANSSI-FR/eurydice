if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eurydice.origin.config.settings.base")
    django.setup()

    from eurydice.origin.cleaning.file_remover import file_remover

    file_remover.OriginFileRemover().start()

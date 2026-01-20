if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "eurydice.destination.config.settings.base")
    django.setup()

    from eurydice.destination.cleaning.file_remover import file_remover

    file_remover.DestinationFileRemover().start()

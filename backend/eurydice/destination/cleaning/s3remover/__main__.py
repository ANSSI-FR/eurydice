if __name__ == "__main__":
    import os

    import django

    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "eurydice.destination.config.settings.base"
    )
    django.setup()

    from eurydice.destination.cleaning.s3remover import s3remover

    s3remover.DestinationS3Remover().start()

from django.urls import include, path

# use DRF error views
# https://www.django-rest-framework.org/api-guide/exceptions/#generic-error-views
from eurydice.common.api.urls import (
    handler400,  # noqa: F401
    handler500,  # noqa: F401
)
from eurydice.common.backoffice import urls as backoffice_urls
from eurydice.common.redoc import urls as redoc_urls
from eurydice.origin.api import urls as api_urls

urlpatterns = [
    path("admin/", include(backoffice_urls)),
    path("api/v1/", include(api_urls)),
    path("api/docs/", include(redoc_urls)),
]

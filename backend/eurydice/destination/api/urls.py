from django.urls import path
from rest_framework import routers

import eurydice.common.api.urls
from eurydice.destination.api import views

router = routers.DefaultRouter()
router.register(
    r"transferables", views.IncomingTransferableViewSet, basename="transferable"
)

urlpatterns = (
    eurydice.common.api.urls.urlpatterns
    + router.urls
    + [
        path("metrics/", views.MetricsView.as_view(), name="metrics"),
        path("status/", views.StatusView.as_view(), name="status"),
        path(
            "user/association/",
            views.UserAssociationView.as_view(),
            name="user-association",
        ),
    ]
)

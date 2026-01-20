from django.urls import path
from rest_framework import routers

import eurydice.common.api.urls
from eurydice.origin.api import views

router = routers.DefaultRouter()
router.register(
    r"transferables",
    views.OutgoingTransferableViewSet,
    basename="transferable",
)

urlpatterns = (
    eurydice.common.api.urls.urlpatterns
    + router.urls
    + [
        path("metrics/", views.MetricsView.as_view(), name="metrics"),
        path("status/", views.StatusView.as_view(), name="status"),
        path("metadata/", views.ServerMetadataView.as_view(), name="server-metadata"),
        path(
            "user/association/",
            views.UserAssociationView.as_view(),
            name="user-association",
        ),
    ]
)

from django.urls import path
from .views import *

urlpatterns = [
    path("event-bookings/", EventBookingViewSet.as_view()),
    path("event-bookings/<int:pk>/", EventBookingGetViewSet.as_view()),
    path(
        "status-change-event-bookings/<int:pk>/",
        StatusChangeEventBookingViewSet.as_view(),
    ),
    path("pending-event-bookings/", PendingEventBookingViewSet.as_view()),
    path("get-all/",GetAllEvent.as_view())
]
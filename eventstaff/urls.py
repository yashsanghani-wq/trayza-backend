from django.urls import path
from .views import StaffViewSet, EventStaffAssignmentViewSet, StaffRoleViewSet

urlpatterns = [
    # Staff Role URLs
    path(
        "roles/",
        StaffRoleViewSet.as_view({"get": "list", "post": "create"}),
        name="staffrole-list",
    ),
    path(
        "roles/<int:pk>/",
        StaffRoleViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="staffrole-detail",
    ),
    # Staff URLs
    path(
        "staff/",
        StaffViewSet.as_view({"get": "list", "post": "create"}),
        name="staff-list",
    ),
    path(
        "staff/<int:pk>/",
        StaffViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="staff-detail",
    ),
    # Event Staff Assignment Custom Action URLs
    path(
        "event-assignments/event-summary/",
        EventStaffAssignmentViewSet.as_view({"get": "event_summary"}),
        name="eventstaffassignment-event-summary",
    ),
    # Event Staff Assignment URLs
    path(
        "event-assignments/",
        EventStaffAssignmentViewSet.as_view({"get": "list", "post": "create"}),
        name="eventstaffassignment-list",
    ),
    path(
        "event-assignments/<int:pk>/",
        EventStaffAssignmentViewSet.as_view(
            {
                "get": "retrieve",
                "put": "update",
                "patch": "partial_update",
                "delete": "destroy",
            }
        ),
        name="eventstaffassignment-detail",
    ),
]

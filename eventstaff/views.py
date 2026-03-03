from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Sum, Count, Q
from .models import Staff, EventStaffAssignment, StaffRole
from .serializers import (
    StaffSerializer,
    EventStaffAssignmentSerializer,
    StaffRoleSerializer,
)
from eventbooking.models import EventBooking


class StaffRoleViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Staff Roles (e.g. Waiter, Manager, Chef)
    """

    queryset = StaffRole.objects.all().order_by("name")
    serializer_class = StaffRoleSerializer
    # permission_classes = [IsAuthenticated] # Uncomment once authentication is strictly enforced
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    search_fields = ["name"]
    ordering_fields = ["name", "created_at"]


class StaffViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Staff
    """

    queryset = Staff.objects.all().order_by("-created_at")
    serializer_class = StaffSerializer
    # permission_classes = [IsAuthenticated] # Uncomment once authentication is strictly enforced
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["role", "staff_type", "is_active"]
    search_fields = ["name", "phone"]
    ordering_fields = ["name", "created_at", "per_person_rate"]


class EventStaffAssignmentViewSet(viewsets.ModelViewSet):
    """
    CRUD API for Event Staff Assignments
    """

    queryset = (
        EventStaffAssignment.objects.select_related(
            "staff", "session", "session__booking"
        )
        .all()
        .order_by("-created_at")
    )
    serializer_class = EventStaffAssignmentSerializer
    # permission_classes = [IsAuthenticated] # Uncomment once authentication is strictly enforced
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = [
        "session",
        "payment_status",
        "staff__staff_type",
    ]
    search_fields = ["staff__name", "session__booking__name"]
    ordering_fields = ["created_at", "total_amount", "paid_amount"]

    @action(detail=False, methods=["get"], url_path="event-summary")
    def event_summary(self, request):
        """
        Return event-wise summary: total labor count, total waiter count, total payment, total paid, total pending
        """
        events = (
            EventBooking.objects.annotate(
                total_labor=Count(
                    "sessions__staff_assignments",
                    filter=Q(sessions__staff_assignments__role_at_event__name="Labor"),
                ),
                total_waiter=Count(
                    "sessions__staff_assignments",
                    filter=Q(sessions__staff_assignments__role_at_event__name="Waiter"),
                ),
                total_amount=Sum("sessions__staff_assignments__total_amount"),
                total_paid=Sum("sessions__staff_assignments__paid_amount"),
                total_pending=Sum("sessions__staff_assignments__remaining_amount"),
            )
            .filter(sessions__staff_assignments__isnull=False)
            .distinct()
            .order_by("-date")
        )

        page = self.paginate_queryset(events)
        data = []
        iterable = page if page is not None else events

        for event in iterable:
            data.append(
                {
                    "event_id": event.id,
                    "event_name": event.name,
                    "event_date": event.date,
                    "total_labor": event.total_labor,
                    "total_waiter": event.total_waiter,
                    "total_amount": (
                        float(event.total_amount) if event.total_amount else 0.0
                    ),
                    "total_paid": float(event.total_paid) if event.total_paid else 0.0,
                    "total_pending": (
                        float(event.total_pending) if event.total_pending else 0.0
                    ),
                }
            )

        if page is not None:
            return self.get_paginated_response(data)

        return Response(
            {
                "status": True,
                "message": "Event staff summary fetched successfully",
                "data": data,
            }
        )

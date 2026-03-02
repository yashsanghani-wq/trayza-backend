from django.contrib import admin
from django.db.models import Sum, Count, Q
from .models import Staff, EventStaffAssignment
from eventbooking.models import EventBooking


@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "phone",
        "role",
        "staff_type",
        "is_active",
        "per_person_rate",
    )
    list_filter = ("role", "staff_type", "is_active")
    search_fields = ("name", "phone")
    list_editable = ("is_active",)


@admin.register(EventStaffAssignment)
class EventStaffAssignmentAdmin(admin.ModelAdmin):
    list_display = (
        "event",
        "staff",
        "role_at_event",
        "total_days",
        "total_amount",
        "paid_amount",
        "remaining_amount",
        "payment_status",
    )
    list_filter = ("payment_status", "event", "staff__staff_type", "role_at_event")
    search_fields = ("event__name", "staff__name")
    readonly_fields = ("total_amount", "remaining_amount", "payment_status")

    fieldsets = (
        (
            "Assignment Details",
            {
                "fields": (
                    "event",
                    "staff",
                    "role_at_event",
                    "total_days",
                    "per_person_rate",
                )
            },
        ),
        (
            "Payment Tracking (Auto-Calculated)",
            {
                "fields": (
                    "total_amount",
                    "paid_amount",
                    "remaining_amount",
                    "payment_status",
                )
            },
        ),
    )

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)


# To add summary functions to Event detail page without modifying eventbooking app directly
# We can create a proxy model or inline admin, but for the event page list view:


class EventStaffAssignmentInline(admin.TabularInline):
    model = EventStaffAssignment
    extra = 1
    readonly_fields = ("total_amount", "remaining_amount", "payment_status")
    fields = (
        "staff",
        "role_at_event",
        "total_days",
        "per_person_rate",
        "total_amount",
        "paid_amount",
        "remaining_amount",
        "payment_status",
    )

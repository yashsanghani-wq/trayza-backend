from rest_framework import serializers
from .models import *


class EventSessionSerializer(serializers.ModelSerializer):
    event_date = serializers.DateField(
        input_formats=["%d-%m-%Y"],  # Accept DD-MM-YYYY in the payload
        format="%d-%m-%Y",  # Return DD-MM-YYYY in the response
    )
    managers_assigned = serializers.SerializerMethodField()
    summoned_staff_details = serializers.SerializerMethodField()

    class Meta:
        model = EventSession
        fields = [
            "id",
            "event_date",
            "event_time",
            "event_address",
            "per_dish_amount",
            "estimated_persons",
            "selected_items",
            "extra_service_amount",
            "extra_service",
            "managers_assigned",
            "summoned_staff_details",
        ]

    def get_managers_assigned(self, obj):
        managers = []
        for assignment in obj.staff_assignments.all():
            role_name = (
                assignment.role_at_event.name
                if assignment.role_at_event
                else (assignment.staff.role.name if assignment.staff.role else "")
            )
            if role_name.lower() == "manager":
                managers.append(assignment.staff.name)
        return managers

    def get_summoned_staff_details(self, obj):
        summoned_staff = []
        for assignment in obj.staff_assignments.all():
            role_name = (
                assignment.role_at_event.name
                if assignment.role_at_event
                else (assignment.staff.role.name if assignment.staff.role else "")
            )
            if assignment.staff.staff_type in ["Agency", "Contract"]:
                summoned_staff.append(
                    {
                        "assignment_id": assignment.id,
                        "name": assignment.staff.name,
                        "staff_type": assignment.staff.staff_type,
                        "people_summoned": assignment.number_of_persons,
                        "role": role_name,
                    }
                )
        return summoned_staff


class EventBookingSerializer(serializers.ModelSerializer):
    advance_amount = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, default=""
    )
    advance_payment_mode = serializers.CharField(
        required=False, allow_blank=True, allow_null=True, default=""
    )
    date = serializers.DateField(
        format="%d-%m-%Y", read_only=True  # Format for response
    )
    sessions = EventSessionSerializer(many=True, required=False)

    class Meta:
        model = EventBooking
        fields = [
            "id",  # Include the primary key for reference
            "name",
            "mobile_no",
            "date",
            "reference",
            "status",
            "advance_amount",
            "advance_payment_mode",
            "description",
            "rule",
            "sessions",
        ]

    def create(self, validated_data):
        sessions_data = validated_data.pop("sessions", [])
        booking = EventBooking.objects.create(**validated_data)
        for session_data in sessions_data:
            EventSession.objects.create(booking=booking, **session_data)
        return booking

    def update(self, instance, validated_data):
        sessions_data = validated_data.pop("sessions", None)

        # update regular booking fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        # If sessions were provided in update, we overwrite old sessions
        # (This is a simplified approach: delete old and create new)
        if sessions_data is not None:
            instance.sessions.all().delete()
            for session_data in sessions_data:
                EventSession.objects.create(booking=instance, **session_data)

        return instance

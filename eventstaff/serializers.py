from rest_framework import serializers
from .models import Staff, EventStaffAssignment, StaffRole


class StaffRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = StaffRole
        fields = "__all__"


class StaffSerializer(serializers.ModelSerializer):
    role_name = serializers.CharField(source="role.name", read_only=True)

    class Meta:
        model = Staff
        fields = "__all__"
        extra_kwargs = {
            "role": {"help_text": "ID of the StaffRole from /eventstaff/roles/"},
            "staff_type": {"help_text": "Type of employment (Fixed, Agency, Contract)"},
            "per_person_rate": {
                "help_text": "Default rate charged per person for this staff member"
            },
        }


class EventStaffAssignmentSerializer(serializers.ModelSerializer):
    # Optional nested details for GET endpoints
    staff_name = serializers.CharField(source="staff.name", read_only=True)
    staff_type = serializers.CharField(source="staff.staff_type", read_only=True)
    session_name = serializers.CharField(source="session.booking.name", read_only=True)
    session_date = serializers.CharField(source="session.event_date", read_only=True)
    role_name_at_event = serializers.CharField(
        source="role_at_event.name", read_only=True
    )

    class Meta:
        model = EventStaffAssignment
        fields = "__all__"
        read_only_fields = (
            "total_amount",
            "remaining_amount",
            "payment_status",
            "created_at",
            "updated_at",
        )

    def validate(self, data):
        """
        Custom validation to prevent invalid values.
        """
        paid_amount = data.get("paid_amount", 0)
        total_days = data.get("total_days", 1)
        per_person_rate = data.get("per_person_rate")

        # Check for negative values
        if paid_amount and paid_amount < 0:
            raise serializers.ValidationError(
                {"paid_amount": "Paid amount cannot be negative."}
            )

        if total_days and total_days <= 0:
            raise serializers.ValidationError(
                {"total_days": "Total days must be greater than zero."}
            )

        if per_person_rate is not None and per_person_rate < 0:
            raise serializers.ValidationError(
                {"per_person_rate": "Per person rate cannot be negative."}
            )

        staff = data.get("staff")
        if not staff and self.instance:
            staff = self.instance.staff

        if staff:
            if staff.staff_type == "Fixed":
                calc_amount = staff.fixed_salary if staff.fixed_salary else 0
            else:
                calc_rate = (
                    per_person_rate
                    if per_person_rate is not None
                    else staff.per_person_rate
                )
                number_of_persons = data.get("number_of_persons", getattr(self.instance, 'number_of_persons', 1))
                calc_amount = calc_rate * total_days * number_of_persons

            # Only validate if paid_amount is provided, or if instance already has paid_amount
            if paid_amount is not None and paid_amount > calc_amount:
                raise serializers.ValidationError(
                    {"paid_amount": "Paid amount cannot exceed total amount."}
                )

        return data

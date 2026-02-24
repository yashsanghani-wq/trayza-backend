from rest_framework import serializers
from decimal import Decimal
from eventbooking.models import EventBooking
from .models import *

class PaymentSerializer(serializers.ModelSerializer):
    payment_date = serializers.DateField(
        input_formats=["%d-%m-%Y"],  # Accept DD-MM-YYYY in the payload
        format="%d-%m-%Y",  # Return DD-MM-YYYY in the response
    )
    formatted_event_date = serializers.ReadOnlyField()

    class Meta:
        model = Payment
        fields = [
            "bill_no",
            "total_amount",
            "advance_amount",
            "total_extra_amount",
            "pending_amount",
            "payment_date",
            "transaction_amount",
            "payment_mode",
            "settlement_amount",
            "payment_status",
            "note",
            "formatted_event_date",
            "billed_to_ids",
        ]
        read_only_fields = ["bill_no", "created_at", "updated_at"]

    def validate_billed_to_ids(self, value):
        """
        Validate that all provided booking IDs exist and ensure each ID is used only once.
        """
        if not isinstance(value, list):
            raise serializers.ValidationError("billed_to_ids must be a list")

        if not value:
            raise serializers.ValidationError("At least one booking ID is required")

        existing_ids = set(
            EventBooking.objects.filter(id__in=value).values_list("id", flat=True)
        )
        invalid_ids = set(value) - existing_ids
        if invalid_ids:
            raise serializers.ValidationError(
                f"Invalid booking IDs: {', '.join(map(str, invalid_ids))}"
            )

        # Ensure each booking ID is used only once
        already_billed_ids = set(
            Payment.objects.filter(billed_to_ids__overlap=value).values_list("billed_to_ids", flat=True)
        )
        duplicate_ids = already_billed_ids.intersection(set(value))
        if duplicate_ids:
            raise serializers.ValidationError(
                f"Payments have already been created for booking IDs: {', '.join(map(str, duplicate_ids))}"
            )

        return value

    def to_representation(self, instance):
        data = super().to_representation(instance)
        if isinstance(instance, dict):
            billed_ids = instance.get("billed_to_ids", [])
        else:
            billed_ids = instance.billed_to_ids

        # Fetch event booking details for all billed IDs
        event_bookings = EventBooking.objects.filter(id__in=billed_ids)
        for event_booking in event_bookings:
            if event_booking.extra_service_amount == "0" and all(service.get("extra") for service in event_booking.extra_service):
                event_booking.extra_service_amount = str(sum(int(service.get("amount", 0)) for service in event_booking.extra_service))
                event_booking.save()
        detailed_bookings = [
            {
                "id": booking.id,
                "name": booking.name,
                "mobile_no": booking.mobile_no,
                "date": booking.date.strftime("%d-%m-%Y"),
                "reference": booking.reference,
                "event_date": booking.event_date.strftime("%d-%m-%Y"),
                "event_time": booking.event_time,
                "status": booking.status,
                "event_address": booking.event_address,
                "advance_amount": str(booking.advance_amount),
                "advance_payment_mode": booking.advance_payment_mode,
                "per_dish_amount": str(booking.per_dish_amount),
                "estimated_persons": booking.estimated_persons,
                "extra_service_amount": booking.extra_service_amount,
                "extra_service": booking.extra_service,
                "selected_items": booking.selected_items,
                "description": booking.description,
                "rule" : booking.rule
            }
            for booking in event_bookings
        ]

        data["billed_to_ids"] = detailed_bookings

        # Format decimal fields
        decimal_fields = [
            "total_amount",
            "advance_amount",
            "pending_amount",
            "transaction_amount",
            "settlement_amount",
        ]
        for field in decimal_fields:
            if data.get(field) is not None:
                data[field] = str(Decimal(data[field]))

        # Auto-set payment_status to "Paid" if pending_amount is 0
        if Decimal(data.get("pending_amount", "0")) == Decimal("0"):
            data["payment_status"] = "PAID"

        return data

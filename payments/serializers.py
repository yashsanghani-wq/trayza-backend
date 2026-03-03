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
            "booking",
        ]
        read_only_fields = ["bill_no", "created_at", "updated_at"]

    def to_representation(self, instance):
        data = super().to_representation(instance)

        if instance.booking:
            from eventbooking.serializers import EventBookingSerializer

            data["booking"] = EventBookingSerializer(instance.booking).data
        else:
            data["booking"] = None

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

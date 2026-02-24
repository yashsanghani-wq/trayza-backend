from rest_framework.response import Response
from rest_framework import status, generics
from Expense.models import Expense
from django.db.models import Sum
from trayza.Utils.permissions import *
from .serializers import *


# --------------------    PaymentViewSet    --------------------


class PaymentViewSet(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request):
        payments = Payment.objects.all().order_by("-payment_date")
        serializer = PaymentSerializer(payments, many=True)
        return Response(
            {
                "status": True,
                "message": "Payment list retrieved successfully",
                "data": serializer.data,
            },
            status=status.HTTP_200_OK,
        )

    def post(self, request):
        # Validate the input using the serializer
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            billed_to_ids = data.get("billed_to_ids", [])
            total_amount = data.get("total_amount", 0)
            advance_amount = data.get("advance_amount", 0)
            total_extra_amount = data.get("total_extra_amount", 0)

            # Check if any of the billed_to_ids already have a completed payment
            existing_payments = Payment.objects.filter(
                billed_to_ids__overlap=billed_to_ids, payment_status="PAID"
            )

            if existing_payments.exists():
                # Get the list of IDs that already have payments
                duplicate_ids = []
                for payment in existing_payments:
                    duplicate_ids.extend(
                        set(payment.billed_to_ids) & set(billed_to_ids)
                    )

                return Response(
                    {
                        "status": False,
                        "message": f"Payment already exists for booking IDs: {duplicate_ids}",
                        "data": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Initialize lists
            event_booking_name_list = []
            event_booking_mobile_no_list = []

            # Validate all event bookings exist
            for bill_id in billed_to_ids:
                try:
                    event_booking = EventBooking.objects.get(id=bill_id)
                    event_booking_name_list.append(event_booking.name)
                    event_booking_mobile_no_list.append(event_booking.mobile_no)
                except EventBooking.DoesNotExist:
                    return Response(
                        {
                            "status": False,
                            "message": f"EventBooking with ID {bill_id} does not exist.",
                            "data": {},
                        },
                        status=status.HTTP_200_OK,
                    )

            # Check for partial/unpaid payments and update if found
            payments = Payment.objects.filter(payment_status__in=["PARTIAL", "UNPAID"])
            payment_found = False

            for payment in payments:
                event_bookings = EventBooking.objects.filter(
                    id__in=payment.billed_to_ids
                )
                for event_booking in event_bookings:
                    if (
                        event_booking.name in event_booking_name_list
                        and event_booking.mobile_no in event_booking_mobile_no_list
                    ):
                        # Check for duplicate IDs in the existing payment
                        duplicate_ids = set(payment.billed_to_ids) & set(billed_to_ids)
                        if duplicate_ids:
                            return Response(
                                {
                                    "status": False,
                                    "message": f"Booking IDs is already exist in payment",
                                    "data": {},
                                },
                                status=status.HTTP_200_OK,
                            )

                        # Update the existing payment
                        payment.billed_to_ids.extend(billed_to_ids)
                        payment.total_amount += total_amount
                        payment.advance_amount += advance_amount
                        payment.pending_amount = (
                            payment.total_amount - payment.advance_amount
                        )
                        payment.total_extra_amount += total_extra_amount

                        # Update payment status based on pending amount
                        if payment.pending_amount == 0:
                            payment.payment_status = "PAID"
                        else:
                            payment.payment_status = "PARTIAL"

                        payment.save()
                        payment_found = True
                        break

            if not payment_found:
                # Calculate pending amount for new payment
                pending_amount = total_amount - advance_amount

                # Set payment status based on pending amount
                if pending_amount == 0:
                    data["payment_status"] = "PAID"
                else:
                    data["payment_status"] = "PARTIAL"

                # Create a new payment
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Payment created successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )

            return Response(
                {
                    "status": True,
                    "message": "Payment created successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )

        return Response(
            {
                "status": False,
                "message": "Something went wrong",
                "data": {},
            },
            status=status.HTTP_200_OK,
        )


class EditPaymentViewSet(generics.GenericAPIView):
    serializer_class = PaymentSerializer
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request, pk=None):
        try:
            payment = Payment.objects.get(pk=pk)
            serializer = PaymentSerializer(payment)
            return Response(
                {
                    "status": True,
                    "message": "Payment retrieved successfully",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Payment not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def put(self, request, pk=None):
        try:
            payment = Payment.objects.get(pk=pk)
            request.data["advance_amount"] = str(
                int(request.data.get("transaction_amount")) + payment.advance_amount
            )
            # request.data["transaction_amount"] = str(int(request.data.get("transaction_amount")) + payment.transaction_amount)
            serializer = PaymentSerializer(payment, data=request.data, partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Payment updated successfully",
                        "data": serializer.data,
                    },
                    status=status.HTTP_200_OK,
                )
            return Response(
                {
                    "status": False,
                    "message": "Something went wrong",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Payment not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

    def delete(self, request, pk=None):
        try:
            payment = Payment.objects.get(pk=pk)
            payment.delete()
            return Response(
                {
                    "status": True,
                    "message": "Payment deleted successfully",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )
        except Payment.DoesNotExist:
            return Response(
                {
                    "status": False,
                    "message": "Payment not found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )


class AllTransactionViewSet(generics.GenericAPIView):
    permission_classes = [IsAdminUserOrReadOnly]

    def get(self, request):

        payments = Payment.objects.all()
        expenses = Expense.objects.all()

        if not payments.exists() and not expenses.exists():
            return Response(
                {
                    "status": False,
                    "message": "No transactions found",
                    "data": {},
                },
                status=status.HTTP_200_OK,
            )

        # 🔹 Payment Aggregation
        total_payment_amount = (
            payments.aggregate(total=Sum("total_amount"))["total"] or 0
        )

        total_paid_amount = 0
        total_unpaid_amount = 0
        total_settlement_amount = 0

        for payment in payments:
            if payment.payment_status == "PAID":
                total_paid_amount += payment.total_amount
            elif payment.payment_status in ["UNPAID", "PARTIAL"]:
                total_unpaid_amount += payment.pending_amount
                total_paid_amount += payment.advance_amount

            total_settlement_amount += payment.settlement_amount

        # 🔹 Expense Aggregation
        total_expense_amount = expenses.aggregate(total=Sum("amount"))["total"] or 0

        # 🔹 Net Calculation (Payment - Expense)
        net_amount = total_payment_amount - total_expense_amount

        final_response = {
            "net_amount": int(net_amount),
            "total_paid_amount": int(total_paid_amount),
            "total_unpaid_amount": int(total_unpaid_amount),
            "total_settlement_amount": int(total_settlement_amount),
            "total_expense_amount": int(total_expense_amount),
        }

        return Response(
            {
                "status": True,
                "message": "Transaction summary",
                "data": final_response,
            },
            status=status.HTTP_200_OK,
        )

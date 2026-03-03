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
        serializer = PaymentSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.validated_data
            booking = data.get("booking")
            if not booking:
                return Response(
                    {"status": False, "message": "booking is required", "data": {}},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            total_amount = data.get("total_amount", 0)
            advance_amount = data.get("advance_amount", 0)
            total_extra_amount = data.get("total_extra_amount", 0)

            # Check if this booking already has a PAID payment
            existing_paid = Payment.objects.filter(
                booking=booking, payment_status="PAID"
            ).first()
            if existing_paid:
                return Response(
                    {
                        "status": False,
                        "message": "Payment already exists and is fully paid for this booking.",
                        "data": {},
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Check for partial/unpaid payments for THIS booking
            existing_payment = Payment.objects.filter(
                booking=booking, payment_status__in=["PARTIAL", "UNPAID"]
            ).first()
            if existing_payment:
                # Update the existing payment
                existing_payment.total_amount += total_amount
                existing_payment.advance_amount += advance_amount
                existing_payment.pending_amount = (
                    existing_payment.total_amount - existing_payment.advance_amount
                )
                existing_payment.total_extra_amount += total_extra_amount

                if existing_payment.pending_amount <= 0:
                    existing_payment.payment_status = "PAID"
                else:
                    existing_payment.payment_status = "PARTIAL"

                existing_payment.save()
                return Response(
                    {
                        "status": True,
                        "message": "Payment updated successfully",
                        "data": PaymentSerializer(existing_payment).data,
                    },
                    status=status.HTTP_200_OK,
                )
            else:
                # Calculate pending amount for new payment
                pending_amount = total_amount - advance_amount
                if pending_amount <= 0:
                    data["payment_status"] = "PAID"
                else:
                    data["payment_status"] = "PARTIAL"

                payment = serializer.save()
                return Response(
                    {
                        "status": True,
                        "message": "Payment created successfully",
                        "data": PaymentSerializer(payment).data,
                    },
                    status=status.HTTP_200_OK,
                )

        return Response(
            {"status": False, "message": "Something went wrong", "data": {}},
            status=status.HTTP_400_BAD_REQUEST,
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

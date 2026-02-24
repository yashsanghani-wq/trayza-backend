from django.db import models

class Payment(models.Model):
    PAYMENT_MODE_CHOICES = [
        ("CASH", "CASH"),
        ("CHEQUE", "CHEQUE"),
        ("BANK_TRANSFER", "BANK TRANSFER"),
        ("ONLINE", "ONLINE"),
        ("OTHER", "OTHER"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PARTIAL", "Partial"),
        ("UNPAID", "Unpaid"),
        ("PAID", "Paid"),
    ]

    bill_no = models.AutoField(primary_key=True)
    # Array field for storing multiple billed_to IDs
    billed_to_ids = models.JSONField(
        default=list, help_text="List of EventBooking IDs this Payment is billed to"
    )
    total_amount = models.DecimalField(max_digits=100, decimal_places=0)
    total_extra_amount = models.DecimalField(max_digits=250, decimal_places=0)
    advance_amount = models.DecimalField(max_digits=100, decimal_places=0)
    pending_amount = models.DecimalField(
        max_digits=100, decimal_places=0, null=True, blank=True
    )
    payment_date = models.DateField()
    transaction_amount = models.DecimalField(max_digits=100, decimal_places=0)
    payment_mode = models.CharField(
        max_length=200, choices=PAYMENT_MODE_CHOICES, default="OTHER"
    )
    settlement_amount = models.DecimalField(
        max_digits=100, decimal_places=0, null=True, blank=True
    )
    payment_status = models.CharField(
        max_length=100, choices=PAYMENT_STATUS_CHOICES, default="UNPAID"
    )
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rule = models.BooleanField(default=False)

    def __str__(self):
        return f"Payment {self.bill_no}"

    @property
    def formatted_event_date(self):
        return self.payment_date.strftime("%d-%m-%Y")

    def save(self, *args, **kwargs):
        # Ensure billed_to_ids is always a list
        if self.billed_to_ids and not isinstance(self.billed_to_ids, list):
            self.billed_to_ids = list(self.billed_to_ids)
        super().save(*args, **kwargs)

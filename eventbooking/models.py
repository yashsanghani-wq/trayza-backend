from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone


class EventBooking(models.Model):
    ADVANCE_PAYMENT_MODE_CHOICES = [
        ("CASH", "CASH"),
        ("CHEQUE", "CHEQUE"),
        ("BANK_TRANSFER", "BANK TRANSFER"),
        ("ONLINE", "ONLINE"),
        ("OTHER", "OTHER"),
    ]
    # Status choices
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirm", "Confirm"),
        ("completed", "Completed"),
        ("cancelled", "Cancelled"),
        ("done", "Done"),
    ]
    # Basic information
    name = models.CharField(max_length=100)
    mobile_no = models.CharField(max_length=17)
    date = models.DateField(default=timezone.now)  # Booking creation date
    reference = models.CharField(max_length=50, unique=False)

    # Advance payment fields (now nullable)
    advance_amount = models.CharField(
        max_length=150, null=True, blank=True  # Allows NULL values in the database
    )
    advance_payment_mode = models.CharField(
        max_length=20, choices=ADVANCE_PAYMENT_MODE_CHOICES, null=True, blank=True
    )

    # Additional details
    description = models.TextField(blank=True)
    # Status field
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    rule = models.BooleanField(default=False)

    class Meta:
        ordering = ["-date"]

    def __str__(self):
        return f"{self.name} - {self.date}"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EventSession(models.Model):
    booking = models.ForeignKey(
        EventBooking, on_delete=models.CASCADE, related_name="sessions"
    )

    # Event details
    event_date = models.DateField()
    event_time = models.CharField(max_length=100)
    event_address = models.TextField(blank=True)

    # Session specifics
    per_dish_amount = models.CharField(max_length=150, blank=True, null=True)
    estimated_persons = models.CharField(max_length=150, blank=True, null=True)

    # Menu items for this specific session
    selected_items = models.JSONField(default=dict)

    # Extra services for this specific session
    extra_service_amount = models.CharField(max_length=250, blank=True, null=True)
    extra_service = models.JSONField(default=dict)

    # Vendors assigned to ingredients
    assigned_vendors = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["event_date", "event_time"]

    def __str__(self):
        return (
            f"Session for {self.booking.name} on {self.event_date} at {self.event_time}"
        )

    @property
    def formatted_event_date(self):
        return self.event_date.strftime("%d-%m-%Y")

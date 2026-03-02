from django.db import models
from decimal import Decimal
from eventbooking.models import EventBooking


class StaffRole(models.Model):
    name = models.CharField("Role Name", max_length=100, unique=True)
    description = models.TextField("Role Description", blank=True, null=True)
    import django.utils.timezone

    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff Role"
        verbose_name_plural = "Staff Roles"

    def __str__(self):
        return self.name


class Staff(models.Model):
    STAFF_TYPE_CHOICES = (
        ("Fixed", "Fixed"),
        ("Agency", "Agency"),
        ("Contract", "Contract"),
    )

    name = models.CharField("Staff Name", max_length=150)
    phone = models.CharField("Phone Number", max_length=20, blank=True, null=True)
    role = models.ForeignKey(StaffRole, on_delete=models.RESTRICT, verbose_name="Role")
    staff_type = models.CharField(
        "Staff Type", max_length=20, choices=STAFF_TYPE_CHOICES, default="Contract"
    )

    fixed_salary = models.DecimalField(
        "Fixed Salary", max_digits=10, decimal_places=2, blank=True, null=True
    )
    per_person_rate = models.DecimalField(
        "Paid Per Person (Rate)", max_digits=10, decimal_places=2, default=0.00
    )
    is_active = models.BooleanField("Is Active", default=True)
    import django.utils.timezone

    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Staff"
        verbose_name_plural = "Staff Members"

    def __str__(self):
        return f"{self.name} ({self.role.name if self.role else 'Unassigned'} - {self.staff_type})"


class EventStaffAssignment(models.Model):
    PAYMENT_STATUS_CHOICES = (
        ("Pending", "Pending"),
        ("Partial", "Partial"),
        ("Paid", "Paid"),
    )

    event = models.ForeignKey(
        EventBooking,
        on_delete=models.CASCADE,
        related_name="staff_assignments",
        verbose_name="Event",
    )
    staff = models.ForeignKey(
        Staff,
        on_delete=models.CASCADE,
        related_name="event_assignments",
        verbose_name="Staff",
    )

    role_at_event = models.ForeignKey(
        StaffRole,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Role at Event",
        help_text="Override default role for this specific event if needed",
    )
    total_days = models.DecimalField(
        "Total Days", max_digits=5, decimal_places=1, default=1.0
    )
    per_person_rate = models.DecimalField(
        "Per Person Rate (Override)",
        max_digits=10,
        decimal_places=2,
        blank=True,
        null=True,
        help_text="Leave blank to use staff's default rate",
    )

    total_amount = models.DecimalField(
        "Total Amount", max_digits=10, decimal_places=2, default=0.00, editable=False
    )
    paid_amount = models.DecimalField(
        "Paid Amount", max_digits=10, decimal_places=2, default=0.00
    )
    remaining_amount = models.DecimalField(
        "Remaining Amount",
        max_digits=10,
        decimal_places=2,
        default=0.00,
        editable=False,
    )
    payment_status = models.CharField(
        "Payment Status",
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="Pending",
        editable=False,
    )
    import django.utils.timezone

    created_at = models.DateTimeField(default=django.utils.timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Event Staff Assignment"
        verbose_name_plural = "Event Staff Assignments"
        unique_together = ("event", "staff")

    def __str__(self):
        return f"{self.staff.name} at {self.event.event_name if hasattr(self.event, 'event_name') else self.event.id}"

    def save(self, *args, **kwargs):
        # 1. Determine effective calculation based on Staff Type
        if self.staff.staff_type == "Fixed":
            # For "Fixed" staff, the pay is simply their fixed salary
            # (ignoring total_days and per_day_rate overrides)
            self.total_amount = (
                self.staff.fixed_salary if self.staff.fixed_salary else Decimal("0.00")
            )

            # If the user tries to override the per_person_rate for a Fixed staff, clear it
            if self.per_person_rate is not None:
                self.per_person_rate = None

        else:
            # For "Agency" or "Contract", pay is per person rate * total_days
            effective_rate = (
                self.per_person_rate
                if self.per_person_rate is not None
                else self.staff.per_person_rate
            )
            self.total_amount = Decimal(str(self.total_days)) * Decimal(
                str(effective_rate)
            )

        # 3. Prevent overpayment logically, though sometimes it happens, keeping it simple here
        if self.paid_amount is None:
            self.paid_amount = Decimal("0.00")

        # 4. Automatically calculate remaining_amount
        self.remaining_amount = self.total_amount - Decimal(str(self.paid_amount))

        # 5. Automatically determine payment_status
        if self.paid_amount <= 0:
            self.payment_status = "Pending"
        elif self.paid_amount >= self.total_amount:
            self.payment_status = "Paid"
        else:
            self.payment_status = "Partial"

        # Default role to staff's default if not provided
        if not self.role_at_event:
            self.role_at_event = self.staff.role

        super().save(*args, **kwargs)

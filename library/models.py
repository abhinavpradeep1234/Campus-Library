from django.db import models
from datetime import timedelta
from django.utils import timezone
from users.models import CustomUser
from users.utils import create_notification


# Create your models here.
class Library(models.Model):
    book_name = models.CharField(max_length=200)
    book_author = models.CharField(max_length=200)
    languages = models.CharField(max_length=200)
    image = models.ImageField(upload_to="new_library", null=True)
    category = models.CharField(max_length=200)
    book_id = models.CharField(max_length=20, unique=True, null=True)
    is_available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.book_name} - {self.book_id}"


class Booking(models.Model):
    STATUS = (
        ("returned", "Returned"),
        ("on hold", "On Hold"),
        ("issued", "Issued"),
    )
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    book_name = models.ForeignKey(Library, on_delete=models.CASCADE)
    date_issue = models.DateTimeField(editable=False)
    due_date = models.DateTimeField(null=True, blank=True)
    fine = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(max_length=50, choices=STATUS, default="on hold")
    returned_date = models.DateField(editable=False, blank=True, null=True)
    status_changed_date = models.DateTimeField(null=True, blank=True)  # New field

    def save(self, *args, **kwargs):
        # If the booking is being created (new record), set the date_issue
        if not self.pk:  # If it's a new record
            self.date_issue = (
                timezone.now()
            )  # Set date_issue when the booking is created

        # Check if the status has changed and update status_changed_date
        if self.pk:  # If the record already exists
            original = Booking.objects.get(pk=self.pk)
            if original.status != self.status:  # Only if status is changing
                self.status_changed_date = timezone.now()

                # Only set the due_date when the status changes
                if not self.due_date:  # If due_date is not set
                    self.due_date = self.status_changed_date + timedelta(
                        minutes=1
                    )  # Add time for due_date

        # Fine calculation: Calculate fine only if due_date is set and overdue
        if self.due_date and self.due_date < timezone.now():
            minutes_overdue = (
                timezone.now() - self.due_date
            ).seconds // 60  # Calculate minutes overdue
            self.fine = minutes_overdue * 10  # Fine of Rs. 10 per minute

            # Send a notification if a fine is generated
            if self.fine > 0:
                notification_message = f"You have an overdue fine of Rs. {self.fine} for '{self.book_name.book_name}'. Please return it as soon as possible."
                create_notification(self.username, notification_message)
        else:
            self.fine = 0

        # If the status is "returned", set the returned_date and stop fine calculation
        if self.status == "returned" and not self.returned_date:
            self.returned_date = timezone.now()
            self.fine = 0  # Stop accumulating the fine when returned

        # If the status is changed back to "issued", resume fine calculation
        if self.status == "issued" and self.fine == 0:
            # Start fine calculation from the last due_date (if available)
            if self.due_date and self.due_date < timezone.now():
                minutes_overdue = (timezone.now() - self.due_date).seconds // 60
                self.fine = minutes_overdue * 10  # Resume fine calculation if overdue

        # Ensure that due_date is always set before saving
        if not self.due_date and self.status_changed_date:
            # If due_date is still not set, calculate it from status_changed_date
            self.due_date = self.status_changed_date + timedelta(
                minutes=1
            )  # Default: 1 minute after status change

        super(Booking, self).save(*args, **kwargs)  # Save the instance


class BookReservation(models.Model):
    BOOKINGSTATUS = (("confirm booking", "Confirm Booking"),)
    STATUS = (
        ("returned", "Returned"),
        ("on hold", "On Hold"),
        ("issued", "Issued"),
    )
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    book_name = models.ForeignKey(Library, on_delete=models.CASCADE)
    reserved_date = models.DateTimeField(editable=False)
    due_date = models.DateTimeField(null=True, blank=True)
    fine = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(max_length=50, choices=STATUS, default="on hold")
    booking_status = models.CharField(max_length=50, choices=BOOKINGSTATUS, null=True)

    returned_date = models.DateField(editable=False, blank=True, null=True)
    status_changed_date = models.DateTimeField(null=True, blank=True)  # New field

    def save(self, *args, **kwargs):
        # If the booking is being created (new record), set the date_issue
        if not self.pk:  # If it's a new record
            self.reserved_date = (
                timezone.now()
            )  # Set date_issue when the booking is created

        # Check if the status has changed and update status_changed_date
        if self.pk:  # If the record already exists
            original = BookReservation.objects.get(pk=self.pk)
            if original.status != self.status:  # Only if status is changing
                self.status_changed_date = timezone.now()

                # Only set the due_date when the status changes
                if not self.due_date:  # If due_date is not set
                    self.due_date = self.status_changed_date + timedelta(
                        minutes=1
                    )  # Add time for due_date

        # Fine calculation: Calculate fine only if due_date is set and overdue
        if self.due_date and self.due_date < timezone.now():
            minutes_overdue = (
                timezone.now() - self.due_date
            ).seconds // 60  # Calculate minutes overdue
            self.fine = minutes_overdue * 10  # Fine of Rs. 10 per minute

            # Send a notification if a fine is generated
            if self.fine > 0:
                notification_message = f"You have an overdue fine of Rs. {self.fine} for '{self.book_name.book_name}'. Please return it as soon as possible."
                create_notification(self.username, notification_message)
        else:
            self.fine = 0

        # If the status is "returned", set the returned_date and stop fine calculation
        if self.status == "returned" and not self.returned_date:
            self.returned_date = timezone.now()
            self.fine = 0  # Stop accumulating the fine when returned

        # If the status is changed back to "issued", resume fine calculation
        if self.status == "issued" and self.fine == 0:
            # Start fine calculation from the last due_date (if available)
            if self.due_date and self.due_date < timezone.now():
                minutes_overdue = (timezone.now() - self.due_date).seconds // 60
                self.fine = minutes_overdue * 10  # Resume fine calculation if overdue

        # Ensure that due_date is always set before saving
        if not self.due_date and self.status_changed_date:
            # If due_date is still not set, calculate it from status_changed_date
            self.due_date = self.status_changed_date + timedelta(
                minutes=1
            )  # Default: 1 minute after status change

        super(BookReservation, self).save(*args, **kwargs)  # Save the instance


class Complaints(models.Model):
    username = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    book_name = models.ForeignKey(
        Library, on_delete=models.CASCADE, null=True, blank=True
    )
    date = models.DateTimeField(auto_now=True, editable=False)
    report_issue = models.CharField(max_length=200, null=True)
    responds = models.CharField(max_length=250, null=True, blank=True)

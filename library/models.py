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
    due_date = models.DateTimeField(editable=False)
    fine = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(max_length=50, choices=STATUS, default="on hold")
    returned_date = models.DateField(editable=False, blank=True, null=True)
    issued_date = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set due_date if it's not already set
        if not self.due_date:
            if not self.date_issue:
                self.date_issue = timezone.now()
            self.due_date = self.date_issue + timedelta(
                minutes=1
            )  # Short duration for testing

        # Calculate the fine if the due date is past
        if self.due_date < timezone.now():
            minutes_overdue = (
                timezone.now() - self.due_date
            ).seconds // 60  # Calculate in minutes
            self.fine = minutes_overdue * 10  # Fine of Rs. 10 per minute

            # Send a notification if a fine is generated
            if self.fine > 0:
                notification_message = f"You have an overdue fine of Rs. {self.fine} for '{self.book_name.book_name}'. Please return it as soon as possible."
                create_notification(self.username, notification_message)
        else:
            self.fine = 0
        if self.status == "returned" and not self.returned_date:
            self.returned_date = timezone.now()

        super(Booking, self).save(*args, **kwargs)


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

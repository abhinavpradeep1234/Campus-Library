from typing import Iterable
from django.db import models
from datetime import timedelta
from django.utils import timezone
from users.models import CustomUser
from django.core.exceptions import ValidationError
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
    )
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    email = models.EmailField(null=True, blank=True)
    book_name = models.ForeignKey(Library, on_delete=models.CASCADE)
    date_issue = models.DateTimeField(editable=False)
    due_date = models.DateTimeField(editable=False)
    fine = models.PositiveIntegerField(default=0, editable=False)
    status = models.CharField(max_length=50, choices=STATUS, default="on hold")
    returned_date=models.DateTimeField(editable=False,blank=True,null=True)

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
   
        # if self.status == "returned" and self.returned_date is None:
        #     self.returned_date = timezone.now()
        # elif self.status != "returned":
        #     # Reset returned_date if status changes away from 'returned'
        #     self.returned_date = None


        super(Booking, self).save(*args, **kwargs)


class Complaints(models.Model):
    username = models.ForeignKey(CustomUser, on_delete=models.CASCADE,null=True,blank=True)
    book_name = models.ForeignKey(Library, on_delete=models.CASCADE,null=True,blank=True)
    date = models.DateTimeField(auto_now=True, editable=False)
    report_issue = models.CharField(max_length=200,null=True)
    responds=models.CharField(max_length=250,null=True,blank=True)
    
    
# class Respond

    # def save(self, *args, **kwargs):
    #     # Set due_date to 7 days from now if it is not set
    #     if not self.due_date:
    #         if not self.date_issue:  # If date_issue is None
    #             self.date_issue = timezone.now()  # Set it to now
    #         self.due_date = self.date_issue + timedelta(days=7)
    #     super(Booking, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):
    #     # Set due_date to 7 days from now if it is not set
    #     if not self.due_date:
    #         if not self.date_issue:  # If date_issue is None
    #             self.date_issue = timezone.now()  # Set it to now
    #         self.due_date = self.date_issue + timedelta(minutes=2)

    #     # Calculate the fine if the due date is past
    #     if self.due_date < timezone.now():
    #         days_overdue = (timezone.now() - self.due_date).days
    #         self.fine = days_overdue * 10  # Fine of Rs. 10 per day
    #         # self.status = "on hold"  # Update status if overdue
    #     else:
    #         self.fine = 0
    #         # self.status = "on hold"  # Keep it "on hold" if not returned

    #     super(Booking, self).save(*args, **kwargs)

    # def save(self, *args, **kwargs):

    #     if not self.due_date:
    #         if not self.date_issue:
    #             self.date_issue = timezone.now()
    #         self.due_date = self.date_issue + timedelta(minutes=1)  # For testing

    #     print(
    #         f"Date Issued: {self.date_issue}, Due Date: {self.due_date}, Current Time: {timezone.now()}"
    #     )

    #     # Calculate fine if due date is past
    #     if self.due_date < timezone.now():
    #         days_overdue = (
    #             timezone.now() - self.due_date
    #         ).seconds // 60  # Calculate in minutes
    #         self.fine = days_overdue * 10  # Fine of Rs. 10 per minute
    #     else:
    #         self.fine = 0

    #     print(f"Calculated Fine: {self.fine}")

    #     # Check if the book is already booked by someone else and is not returned

    #     super(Booking, self).save(*args, **kwargs)

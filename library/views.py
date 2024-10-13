from django.shortcuts import render, redirect
from .models import Library, Booking
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .forms import LibraryForm, BookingForm, UpdateStatusForm
from users.utils import create_notification
from users.models import Notification, CustomUser


# Create your views here.
def library(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    context = {
        "page_title": "View Library",
        "all_books": Library.objects.all(),
        "unread_count": unread_count,
    }
    return render(request, "view_library.html", context)


def add_library(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    if request.method == "POST":
        form = LibraryForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Book Added To Library Successfully ",
                extra_tags="alert-success",
            )
            all_users = CustomUser.objects.filter(is_active=True)
            for user in all_users:
                create_notification(
                    user, "New Book Added To Library  Please check it out"
                )
            return redirect("library")

        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.success(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Add Book",
        "form": LibraryForm(),
        "unread_count": unread_count,
    }

    return render(request, "add_update_libarary.html", context)


def update_library(request, pk):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    to_update = get_object_or_404(
        Library,
        id=pk,
    )
    if request.method == "POST":
        form = LibraryForm(request.POST, request.FILES, instance=to_update)
        if form.is_valid():
            form.save()
            messages.success(
                request,
                "Book Updated To Library  ",
                extra_tags="alert-success",
            )
            return redirect("library")

        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.success(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Update Book",
        "form": LibraryForm(instance=to_update),
        "unread_count": unread_count,
    }

    return render(request, "add_update_libarary.html", context)


def delete_library(request, pk):
    to_delete = get_object_or_404(Library, id=pk)
    to_delete.delete()
    messages.success(request, "Deleted Successfully", extra_tags="alert-success")
    return redirect("library")


def view_booking(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.save()
    context = {
        "page_title": "All Booking",
        "all_bookings": Booking.objects.all(),
        "form": UpdateStatusForm,
        "unread_count": unread_count,
    }
    return render(request, "view_booking.html", context)


def add_booking(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            book = form.cleaned_data["book_name"]

            # Fetch the book object using the selected book
            # book = Library.objects.get(id=selected_booking.id)  # Ensure you're getting the right book

            if not book.is_available:
                messages.error(
                    request,
                    "The book is already booked by another user, so it's unavailable.",
                    extra_tags="alert-danger",
                )
                context = {
                    "page_title": "Book Now",
                    "form": BookingForm(),
                    "unread_count": unread_count,
                }
                return render(request, "add_booking.html", context)

            # Check if the user already has an active booking
            if Booking.objects.filter(username=request.user).exists():
                messages.error(
                    request,
                    "You already have an active booking. You can't book more than one book.",
                    extra_tags="alert-danger",
                )
                context={"page_title": "Book Now",
                    "form": BookingForm(),
                    "unread_count": unread_count,}
                return render(request, "add_booking.html", context)

            # Proceed with the booking if all checks pass
            booking = form.save(commit=False)
            booking.username = request.user
            booking.save()  # Save the booking first

            # Mark the selected book as unavailable after saving the booking
            book.is_available = False
            book.save()

            messages.success(
                request,
                "Your booking is successful! Check your dashboard, and you can collect the book from the library.",
                extra_tags="alert-success",
            )

            # Create a notification if the user is authenticated
            if request.user.is_authenticated:
                create_notification(
                    request.user,
                    "Booking confirmed! Please visit the library to collect your book.",
                )

            return redirect("dashboard")

        else:
            # Handle form errors
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-danger")

    context = {
        "page_title": "Book Now",
        "form": BookingForm(),
        "unread_count": unread_count,
    }
    return render(request, "add_booking.html", context)


def update_booking(request, pk):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    to_update = get_object_or_404(Booking, id=pk)
    if request.method == "POST":
        form = UpdateStatusForm(request.POST, instance=to_update)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Status Updated successfully", extra_tags="alert-success"
            )
            return redirect("dashboard")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Update Status",
        "form": UpdateStatusForm(instance=to_update),
        "unread_count": unread_count,
    }
    return render(request, "dashboard_user.html", context)


def delete_booking(request, pk):
    to_delete = get_object_or_404(Booking, id=pk)

    # Capture the user before deleting the booking
    user_to_notify = (
        to_delete.username
    )  # Assuming 'username' is the user field in the Booking model

    to_delete.delete()

    messages.success(request, "Removed as Returned ", extra_tags="alert-success")

    # Send notification to the user whose booking was deleted
    if request.user.is_authenticated:
        create_notification(user_to_notify, "Your Returned the Book Thank You...")

    return redirect("dashboard")


def return_status(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.save()
    context = {
        "all_bookings": Booking.objects.filter(status="returned").all(),
        "page_title": "Returned User",
        "form": UpdateStatusForm,
        "unread_count": unread_count,
    }
    return render(request, "status_filter.html", context)


def fine(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.save()
        if request.user.is_authenticated:
            create_notification(request.user, "fine..")

    context = {
        "all_bookings": Booking.objects.filter(fine__gt=0).all(),
        "page_title": "Fine",
        "unread_count": unread_count,
        "form": UpdateStatusForm,
    }
    return render(request, "fine_filter.html", context)


def on_hold(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.save()
    all_bookings = Booking.objects.filter(status="on hold").all()
    context = {
        "page_title": "Hold Users",
        "all_bookings": all_bookings,
        "form": UpdateStatusForm,
        "unread_count": unread_count,
    }
    return render(request, "status_on_hold_filter.html", context)

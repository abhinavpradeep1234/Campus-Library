from django.shortcuts import render, redirect
from library.models import Library, Booking, Complaints

# Respond
from django.shortcuts import get_object_or_404
from django.contrib import messages
from library.forms import (
    LibraryForm,
    BookingForm,
    UpdateStatusForm,
    ComplaintForm,
    RespondComplaintForm,
    UserUpdateStatusForm,
)
from users.utils import create_notification
from users.models import Notification, CustomUser
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView
from django.contrib.auth.decorators import login_required


class LibraryListView(LoginRequiredMixin, ListView):
    model = Library
    template_name = "view_library.html"
    extra_context = {
        "page_title": "View Library",
    }
    context_object_name = "all_books"
    paginate_by = 4
    ordering = ["id"]

    def get_queryset(self):
        # Perform the loop to save all bookings (if necessary)
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()  # Update or process each booking

        # Get the search and filter parameters
        search = self.request.GET.get("search")
        filter_type = self.request.GET.get("search_filter")

        # Start with the base queryset
        queryset = super().get_queryset()

        # Apply search and filtering logic
        if search:
            if filter_type == "book":
                queryset = queryset.filter(book_name__icontains=search)
            elif filter_type == "languages":
                queryset = queryset.filter(languages__icontains=search)
            elif filter_type == "category":
                queryset = queryset.filter(category__icontains=search)

            # Handle the case where no results are found
            if not queryset.exists():
                messages.error(
                    self.request,
                    "Sorry Your Entered Data is Not Found",
                    extra_tags="alert-danger",
                )

        return queryset


@login_required(login_url="signup")
def add_library(request):
    if request.user.role == "ADMIN":
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
    return redirect("404")


@login_required(login_url="signup")
def update_library(request, pk):
    if request.user.role == "ADMIN":
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
    return redirect("404")


@login_required(login_url="signup")
def delete_library(request, pk):
    if request.user.role == "ADMIN":

        to_delete = get_object_or_404(Library, id=pk)
        to_delete.delete()
        messages.success(request, "Deleted Successfully", extra_tags="alert-success")
        return redirect("library")

    return redirect("404")


class BookingListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "view_booking.html"
    context_object_name = "all_bookings"
    paginate_by = 8
    ordering = ["id"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "All Bookings"
        context["form"] = (UpdateStatusForm,)
        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()

        for booking in bookings:
            booking.save()
        return super().get_queryset()


@login_required(login_url="signup")
def add_booking(request, pk):

    all_book = get_object_or_404(Library, id=pk)
    booking_limit = Booking.objects.filter(username=request.user).count()
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    available_booking = Library.objects.filter(is_available=True)
    if not available_booking:
        messages.error(
            request,
            "Currently No Books Are Available .",
            extra_tags="alert-danger",
        )

    if request.method == "POST":
        form = BookingForm(request.POST)
        if form.is_valid():
            if booking_limit >= 3:
                messages.error(
                    request,
                    "You have already reached the limit . You can't book more than three book.",
                    extra_tags="alert-danger",
                )
                context = {
                    "page_title": "Book Now",
                    "form": form,
                    "unread_count": unread_count,
                }
                return render(request, "add_booking.html", context)
            book = form.cleaned_data["book_name"]
            booking = form.save(commit=False)
            booking.username = request.user
            booking.save()
            book.is_available = False
            book.save()
            messages.success(
                request,
                "Your booking is successful! Check your dashboard, and you can collect the book from the library.",
                extra_tags="alert-success",
            )

            # Create a notification if the user is authenticated
            admins = CustomUser.objects.filter(role="ADMIN")
            for admin in admins:
                create_notification(
                    admin,
                    f"user {request.user} Booked a Book {booking.book_name} check it now !!",
                )

            create_notification(
                request.user,
                "Booking confirmed! Please visit the library to collect your book.",
            )

            return redirect("dashboard")

        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-danger")

    initial_data = {"book_name": all_book}
    form = BookingForm(initial_data)

    context = {
        "page_title": "Book Now",
        "form": form,
        "unread_count": unread_count,
        "all_book": all_book,
    }
    return render(request, "add_booking.html", context)


@login_required(login_url="signup")
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
            admin_users = CustomUser.objects.filter(role="ADMIN")
            for admin_user in admin_users:
                Notification.objects.create(
                    username=admin_user,
                    notification=f"The user {request.user.username} has updated their booking status to 'returned'.",
                    is_mark=False,
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


@login_required(login_url="signup")
def delete_booking(request, pk):
    if request.user.role == "ADMIN":
        to_delete = get_object_or_404(Booking, id=pk)
        book_to_update = to_delete.book_name

        # Capture the user before deleting the booking
        user_to_notify = (
            to_delete.username
        )  # Assuming 'username' is the user field in the Booking model

        to_delete.delete()
        book_to_update.is_available = True
        book_to_update.save()

        messages.success(request, "Mark as Returned ", extra_tags="alert-success")

        # Send notification to the user whose booking was deleted
        if request.user.is_authenticated:
            create_notification(user_to_notify, "Your Returned the Book Thank You...")

        return redirect("dashboard")
    return redirect("404")


@login_required(login_url="signup")
def cancel_booking(request, pk):

    to_delete = get_object_or_404(Booking, id=pk)
    book_to_update = to_delete.book_name

    to_delete.delete()
    book_to_update.is_available = True
    book_to_update.save()

    messages.success(request, "You canceled the Book ", extra_tags="alert-success")
    admin = CustomUser.objects.filter(role="ADMIN")
    create_notification(request.user, "Your Booking canceled...")

    for admins in admin:
        create_notification(admins, f"User {to_delete.username} canceled Book...")

    return redirect("dashboard")


class ReturnStatusListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "status_filter.html"
    paginate_by = 8
    ordering = ["id"]

    # context_object_name = "all_bookings"
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Returned Users"
        context["form"] = UpdateStatusForm
        context["all_bookings"] = Booking.objects.filter(status="returned").all()

        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


class FineListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "fine_filter.html"
    paginate_by = 8
    ordering = ["id"]

    # context_object_name = "all_bookings"
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Fined Users"
        context["form"] = UpdateStatusForm
        context["all_bookings"] = Booking.objects.filter(fine__gt=0).all()
        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


class IssuedListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "issued_filter.html"
    paginate_by = 8
    ordering = ["id"]

    # context_object_name = "all_bookings"
    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Issued Users"
        context["form"] = UpdateStatusForm
        context["all_bookings"] = Booking.objects.filter(status="issued").all()
        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


class OnHoldStatusListView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = "status_on_hold_filter.html"
    paginate_by = 8
    ordering = ["id"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Book Hold Users"
        context["form"] = UpdateStatusForm
        context["all_bookings"] = Booking.objects.filter(status="on hold").all()
        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


class ComplaintsListView(LoginRequiredMixin, ListView):
    model = Complaints
    template_name = "view_complaints.html"
    context_object_name = "all_bookings"
    paginate_by = 8
    ordering = ["id"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "View Complaints"
        context["all_bookings"] = Complaints.objects.filter(username=self.request.user)
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


@login_required(login_url="signup")
def add_complaints(request):
    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaints = form.save(commit=False)
            complaints.username = request.user
            complaints.save()
            messages.success(
                request, "Complaint Registered Successfully", extra_tags="alert-success"
            )
            create_notification(
                request.user,
                "Your complaint has been submitted successfully. We'll review it soon.",
            )

            # Notify the admin about the new complaint
            admin_users = CustomUser.objects.filter(role="ADMIN")
            for admin_user in admin_users:
                create_notification(
                    admin_user,
                    f"A new complaint has been submitted by {request.user.username}. Check it now.",
                )

            return redirect("view_complaints")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.success(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Register Complaint",
        "form": ComplaintForm,
        "complaint": True,
    }
    return render(request, "add_booking.html", context)


class AllComplaintsListView(LoginRequiredMixin, ListView):
    model = Complaints
    template_name = "all_complaints.html"
    context_object_name = "all_bookings"
    paginate_by = 8
    ordering = ["id"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "View Complaints"
        context["all_bookings"] = Complaints.objects.all()
        return context

    def get_queryset(self):
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        return super().get_queryset()


@login_required(login_url="signup")
def update_complaints(request, pk):
    to_update = get_object_or_404(Complaints, id=pk)
    if request.method == "POST":
        form = ComplaintForm(request.POST, instance=to_update)
        if form.is_valid():
            complaints = form.save(commit=False)
            complaints.username = request.user
            messages.success(
                request, "Complaint Updated Successfully", extra_tags="alert-success"
            )
            complaints.save()

            return redirect("view_complaints")

        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.success(request, errors, extra_tags="alert-danger")

    context = {
        "page_title": "Edit  Complaint",
        "form": ComplaintForm(instance=to_update),
    }
    return render(request, "add_booking.html", context)


@login_required(login_url="signup")
def delete_complaints(request, pk):
    to_delete = get_object_or_404(Complaints, id=pk)
    to_delete.delete()
    messages.success(request, " You Cancel Complaint", extra_tags="alert-danger")
    return redirect("view_complaints")


@login_required(login_url="signup")
def create_respond(request, pk):
    if request.user.role == "ADMIN":
        to_update = get_object_or_404(Complaints, id=pk)
        notify = to_update.username
        if request.method == "POST":
            form = RespondComplaintForm(request.POST, instance=to_update)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "Add  respond to the complaints",
                    extra_tags="alert-success",
                )
                if request.user.is_authenticated:
                    create_notification(
                        notify,
                        "The Authority has reviewed your Complaint and provided a response.",
                    )

                return redirect("dashboard_admin")
            else:
                for error_list in form.errors.values():
                    for errors in error_list:
                        messages.success(request, errors, extra_tags="alert-danger")

        context = {
            "page_title": "Respond  Complaint",
            "form": RespondComplaintForm(instance=to_update),
        }
        return render(request, "add_update_users.html", context)
    return redirect("404")


# @login_required(login_url="signup")
# def delete_respond(request, pk):
#     to_delete = get_object_or_404(Respond, id=pk)
#     to_delete.delete()
#     messages.success(
#         request, "Add A respond to the complaints", extra_tags="alert-success"
#     )
#     return redirect("admin_dashboard")

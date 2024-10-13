from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, ProfileUpdate
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import CustomUser, Notification

# from django.db import IntegrityError
from library.models import Library
from django.shortcuts import get_object_or_404
from library.forms import UpdateStatusForm
from .forms import RegistrationUserForm
from library.models import Booking
from users.utils import create_notification


def Signup(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():

            user = form.save()
            login(request, user)
            messages.success(
                request,
                "Your Created Account successfully",
                extra_tags="alert-success",
            )
            return redirect("login")

        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-success")
    context = {"page_title": "SignUp", "form": SignupForm}

    return render(request, "signup.html", context)

    # if request.method == "POST":


def log_in(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]
            try:
                user = CustomUser.objects.get(username=username)
            except CustomUser.DoesNotExist:
                messages.error(
                    request, "Username DoesNot Exist", extra_tags="alert-success"
                )

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(
                    request, "You Logged in !!", extra_tags="alert-success"
                )
                return redirect("home")
            else:
                messages.error(request, "Incorrect Password", extra_tags="alert-danger")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-danger")

    context = {"page_title": "Login", "form": LoginForm}

    return render(request, "login.html", context)


def log_out(request):
    messages.success(request, "Logged Out", extra_tags="alert-success")
    return redirect("signup")


def home(request):
    if request.user.is_authenticated:
        create_notification(request.user, "Welcome makkale Adich keri vaaa..")
    return render(request, "index.html")


def profile(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    context = {
        "page_title": "Profile",
        "form": ProfileUpdate(),
        "to_update": request.user,
        "unread_count": unread_count,
    }

    return render(request, "profile.html", context)


def profile_update(request, pk):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    to_update = get_object_or_404(CustomUser, id=pk)
    if request.method == "POST":
        form = ProfileUpdate(request.POST, request.FILES, instance=to_update)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Profile Updated Successfully", extra_tags="alert-success"
            )
            return redirect("profile")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.success(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Update Profile",
        "form": ProfileUpdate(instance=to_update),
        "unread_count": unread_count,
    }
    return render(request, "profile.html", context)


def dashboard(request):
    users = request.user
    if users.role == "ADMIN":
        return redirect("dashboard_admin")
    elif users:
        return redirect("dashboard_user")


def dashboard_user(request):
    username = request.user
    bookings = Booking.objects.filter(username=request.user)

    for booking in bookings:
        booking.save()

    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    context = {
        "page_title": "User Dashboard",
        "all_bookings": Booking.objects.filter(username=username),
        "form": UpdateStatusForm,
        "unread_count": unread_count,
    }
    return render(request, "dashboard_users.html", context)


def dashboard_admin(request):
    bookings = Booking.objects.all()
    for booking in bookings:
        booking.save()
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    admin_count = CustomUser.objects.filter(role="ADMIN").count()
    returned = Booking.objects.filter(status="returned").count()
    hold = Booking.objects.filter(status="on hold").count()
    fine_count = Booking.objects.filter(
        fine__gt=0
    ).count()
   

    context = {
        "page_title": " Admin Dashboard",
        "users": CustomUser.objects.count(),
        "Books": Library.objects.count(),
        "admin_count": admin_count,
        "booked": Booking.objects.count(),
        "returned": returned,
        "hold": hold,
        "form": UpdateStatusForm(),
        "fine": fine_count,
        "unread_count": unread_count,

    }
    return render(request, "admin_dashboard.html", context)


def view_user(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    context = {
        "page_title": " View Registered User",
        "all_users": CustomUser.objects.all(),
        "unread_count": unread_count,
    }
    return render(request, "view_users.html", context)


def add_user(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()

    if request.method == "POST":
        form = RegistrationUserForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(
                request, "You Registered User Successfully", extra_tags="alert-success"
            )
            return redirect("view_user")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-success")
                    return redirect("add_user")
    context = {
        "page_title": "Add User",
        "form": RegistrationUserForm(),
        "unread_count": unread_count,
    }

    return render(request, "add_update_users.html", context)


def delete_user(request, pk=id):

    to_delete = get_object_or_404(CustomUser, id=pk)
    to_delete.delete()
    messages.success(
        request, f" {to_delete} Deleted Successfully ", extra_tags="alert-success"
    )
    return redirect("view_user")


def update_user(request, pk=id):
    to_update = get_object_or_404(CustomUser, id=pk)
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    if request.method == "POST":
        form = RegistrationUserForm(request.POST, instance=to_update)
        if form.is_valid():
            form.save()
            messages.success(
                request, "Updated Successfully", extra_tags="alert-success"
            )
            return redirect("view_user")
        else:
            for error_list in form.errors.values():
                for errors in error_list:
                    messages.error(request, errors, extra_tags="alert-danger")
    context = {
        "page_title": "Update User",
        "form": RegistrationUserForm(instance=to_update),
        "unread_count": unread_count,
    }
    return render(request, "add_update_users.html", context)


def notification(request):
    unread_count = Notification.objects.filter(
        is_mark=False, username=request.user
    ).count()
    context = {
        "page_title": "View Notification",
        "unread_count": unread_count,
        "all_notifications": Notification.objects.filter(
            username=request.user
        ).order_by("-id"),
    }
    return render(request, "notification.html", context)


def mark_as_read(request, pk):
    to_notification = get_object_or_404(Notification, id=pk)
    to_notification.is_mark = True
    to_notification.save()
    return redirect("notification")

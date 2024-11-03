from django.shortcuts import render, redirect

from .forms import SignupForm, LoginForm, ProfileUpdate
from django.contrib import messages
from django.contrib.auth import authenticate, login
from .models import CustomUser, Notification
from django.contrib.auth.decorators import login_required

from django.contrib.auth.mixins import LoginRequiredMixin

# from django.db import IntegrityError
from library.models import Library
from django.shortcuts import get_object_or_404
from library.forms import UpdateStatusForm
from .forms import RegistrationUserForm
from library.models import Booking,Complaints
from users.utils import create_notification

from django.views.generic import ListView


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


@login_required(login_url="signup")
def home(request):
    if request.user.is_authenticated:
        create_notification(request.user, "Welcome To library Explore your book")
    return render(request, "index.html")


@login_required(login_url="login")
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


@login_required(login_url="signup")
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
        # "user": to_update,
    }
    return render(request, "add_update_users.html", context)


@login_required(login_url="signup")
def dashboard(request):
    users = request.user
    if users.role == "ADMIN":
        return redirect("dashboard_admin")
    elif users:
        return redirect("dashboard_user")


@login_required(login_url="signup")
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


@login_required(login_url="signup")
def dashboard_admin(request):
    if request.user.role == "ADMIN":
        bookings = Booking.objects.all()
        for booking in bookings:
            booking.save()
        unread_count = Notification.objects.filter(
            is_mark=False, username=request.user
        ).count()

        admin_count = CustomUser.objects.filter(role="ADMIN").count()
        returned = Booking.objects.filter(status="returned").count()
        hold = Booking.objects.filter(status="on hold").count()
        fine_count = Booking.objects.filter(fine__gt=0).count()

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
            "complaints_count":Complaints.objects.count(),
            "all_bookings":Complaints.objects.all(),
        }
        return render(request, "admin_dashboard.html", context)
    return redirect("404")


class UserListView(LoginRequiredMixin, ListView):
    model = CustomUser
    template_name = "view_users.html"
    context_object_name = "all_users"
    paginate_by = 8
    ordering = ["id"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.role != "ADMIN":
            return redirect("404")

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = " All Registered User"
        context["unread_count"] = Notification.objects.filter(
            is_mark=False, username=self.request.user
        ).count()
        return context


@login_required(login_url="signup")
def add_user(request):
    if request.user.role == "ADMIN":
        unread_count = Notification.objects.filter(
            is_mark=False, username=request.user
        ).count()

        if request.method == "POST":
            form = RegistrationUserForm(request.POST)
            if form.is_valid():
                form.save()
                messages.success(
                    request,
                    "You Registered User Successfully",
                    extra_tags="alert-success",
                )
                return redirect("view_user")
            else:
                for error_list in form.errors.values():
                    for error in error_list:
                        messages.error(request, error, extra_tags="alert-danger")
                return redirect("add_user")

        context = {
            "page_title": "Add User",
            "unread_count": unread_count,
            "form": RegistrationUserForm(),
        }

        return render(request, "add_update_users.html", context)

    return redirect("404")


@login_required(login_url="signup")
def delete_user(request, pk=id):
    if request.user.role == "ADMIN":

        to_delete = get_object_or_404(CustomUser, id=pk)
        to_delete.delete()
        messages.success(
            request, f" {to_delete} Deleted Successfully ", extra_tags="alert-success"
        )
        return redirect("view_user")
    return redirect("404")


@login_required(login_url="signup")
def update_user(request, pk=id):
    if request.user.role == "ADMIN":

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
    return redirect("404")


@login_required(login_url="signup")
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


@login_required(login_url="signup")
def mark_as_read(request, pk):
    to_notification = get_object_or_404(Notification, id=pk)
    to_notification.is_mark = True
    to_notification.save()
    return redirect("notification")


def error_404(request):
    context={"page_title":"403"}
    return render(request, "404.html",context)


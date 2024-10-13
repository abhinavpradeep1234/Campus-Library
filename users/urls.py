from django.urls import path
from . import views

urlpatterns = [
    path("", views.Signup, name="signup"),
    path("users/Login", views.log_in, name="login"),
    path("users/Logout", views.log_out, name="logout"),
    path("Account/Home", views.home, name="home"),
    path("users/Dashboard", views.dashboard, name="dashboard"),
    path("users/Dashboard/admin", views.dashboard_admin, name="dashboard_admin"),
    path("users/Dashboard/user", views.dashboard_user, name="dashboard_user"),
    path("add/user", views.add_user, name="add_user"),
    path("view/user", views.view_user, name="view_user"),
    path("update/user/<int:pk>/", views.update_user, name="update_user"),
    path("delete/user/<int:pk>", views.delete_user, name="delete_user"),
    path("users/Notification", views.notification, name="notification"),
    path(
        "users/Notification/mark_as_read/<int:pk>",
        views.mark_as_read,
        name="mark_as_read",
    ),
    path("Profile/user", views.profile, name="profile"),
    path("Profile/user/update/<int:pk>", views.profile_update, name="profile_update"),
]

from django.urls import path
from . import views

urlpatterns = [
    path("view/library", views.library, name="library"),
    path("add/library", views.add_library, name="add_library"),
    path("update/library/<int:pk>", views.update_library, name="update_library"),
    path("delete/library/<int:pk>", views.delete_library, name="delete_library"),
    path("view/library/booking", views.view_booking, name="view_booking"),
    path("add/library/booking/", views.add_booking, name="add_booking"),
    path(
        "update/library/booking/<int:pk>", views.update_booking, name="update_booking"
    ),
    path("delete/booking/<int:pk>", views.delete_booking, name="delete_booking"),
    path("view/status", views.return_status, name="return_status"),
    path("view/status/on_hold", views.on_hold, name="on_hold"),
    path("view/fine", views.fine, name="fine"),
]

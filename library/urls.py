from django.urls import path
from . import views

urlpatterns = [
    path("library", views.LibraryListView.as_view(), name="library"),
    path("add/library", views.add_library, name="add_library"),
    path("update/library/<int:pk>", views.update_library, name="update_library"),
    path("delete/library/<int:pk>", views.delete_library, name="delete_library"),
    path("library/booking", views.BookingListView.as_view(), name="view_booking"),
    path("add/library/booking/<int:pk>", views.add_booking, name="add_booking"),
    path(
        "update/library/booking/<int:pk>", views.update_booking, name="update_booking"
    ),
    path("delete/booking/<int:pk>", views.delete_booking, name="delete_booking"),
    path("view/status", views.ReturnStatusListView.as_view(), name="return_status"),
    path("view/status/on_hold", views.OnHoldStatusListView.as_view(), name="on_hold"),
    path("view/fine", views.FineListView.as_view(), name="fine"),
    #for user
    path("view/complaints", views.ComplaintsListView.as_view(), name="view_complaints"),
    #for admin
    path("all/complaints", views.AllComplaintsListView.as_view(), name="all_complaints"),
    path("add/complaints", views.add_complaints, name="add_complaints"),
    path(
        "update/complaints/<int:pk>", views.update_complaints, name="update_complaints"
    ),
    path("delete/complaints/<int:pk>", views.delete_complaints, name="delete_complaints"),
]

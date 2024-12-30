from django.urls import path
from . import views

urlpatterns = [
    path("library", views.LibraryListView.as_view(), name="library"),
    path("add/library", views.add_library, name="add_library"),
    path("update/library/<int:pk>", views.update_library, name="update_library"),
    path("delete/library/<int:pk>", views.delete_library, name="delete_library"),
    path("library/booking", views.BookingListView.as_view(), name="view_booking"),
    path("add/library/booking/<int:pk>", views.add_booking, name="add_booking"),
    # reservation
    path(
        "add/library/reservation/<int:pk>",
        views.add_reservation,
        name="add_reservation",
    ),
    # user ststus change
    path(
        "status/reservation/<int:pk>",
        views.user_status_update_reservation,
        name="user_status_reservation",
    ),
    # confirm the booking reservation
    path(
        "status/reservations/<int:pk>",
        views.update_reservation,
        name="update_reservation",
    ),
    # admin ststus change
    path(
        "status/update/reservation/<int:pk>",
        views.status_update_reservation,
        name="status_update_reservation",
    ),
    path(
        "update/library/booking/<int:pk>", views.update_booking, name="update_booking"
    ),
    path("delete/booking/<int:pk>", views.delete_booking, name="delete_booking"),
    path(
        "delete/reservation/<int:pk>",
        views.delete_reservation_booking,
        name="delete_reservation_booking",
    ),
    path("cancel/booking/<int:pk>", views.cancel_booking, name="cancel_booking"),
    path("cancel/reservation/<int:pk>", views.cancel_reservation, name="cancel_reservation"),
    path("view/status", views.ReturnStatusListView.as_view(), name="return_status"),
    path("view/status/on_hold", views.OnHoldStatusListView.as_view(), name="on_hold"),
    path("view/fine", views.FineListView.as_view(), name="fine"),
    path("view/issued", views.IssuedListView.as_view(), name="issued"),
    ### #reservation
    path(
        "view/reserved/status",
        views.ReservedReturnStatusListView.as_view(),
        name="reserved_return_status",
    ),
    path(
        "view/reserved/on_hold",
        views.ReservedOnHoldStatusListView.as_view(),
        name="reserved_on_hold",
    ),
    path(
        "view/reserved/fine", views.ReservedFineListView.as_view(), name="reserved_fine"
    ),
    path(
        "view/reserved/issued",
        views.ReservedIssuedListView.as_view(),
        name="reserved_issued",
    ),
    # for user
    path("view/complaints", views.ComplaintsListView.as_view(), name="view_complaints"),
    # for admin
    path(
        "all/complaints", views.AllComplaintsListView.as_view(), name="all_complaints"
    ),
    path("add/complaints", views.add_complaints, name="add_complaints"),
    path(
        "update/complaints/<int:pk>", views.update_complaints, name="update_complaints"
    ),
    path(
        "delete/complaints/<int:pk>", views.delete_complaints, name="delete_complaints"
    ),
    path(
        "complaints/create/respond/<int:pk>",
        views.create_respond,
        name="create_respond",
    ),
    # path("delete/complaints/<int:pk>", views.delete_respond, name="delete_respond"),
]

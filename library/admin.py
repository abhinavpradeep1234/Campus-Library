from django.contrib import admin
from library.models import Library, Booking,Complaints


# Register your models here.
class LibraryAdmin(admin.ModelAdmin):
    list_display = (
        "book_name",
        "book_author",
        "is_available",
    )


admin.site.register(Library, LibraryAdmin)
admin.site.register(Booking)
admin.site.register(Complaints)

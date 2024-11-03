from django import forms
from .models import Library, Booking, Complaints


class LibraryForm(forms.ModelForm):
    class Meta:
        model = Library
        fields = [
            "book_name",
            "book_author",
            "category",
            "languages",
            "image",
            "is_available",
        ]

        widgets = {
            "book_name": forms.TextInput(attrs={"class": "form-control"}),
            "book_author": forms.TextInput(attrs={"class": "form-control"}),
            "languages": forms.TextInput(attrs={"class": "form-control"}),
            "category": forms.TextInput(attrs={"class": "form-control"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
            "available": forms.CheckboxInput(attrs={"class": "form-select"}),
        }


class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = [
            "book_name",
            "email",
        ]

        widgets = {
            "book_name": forms.Select(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        available_books = Library.objects.filter(is_available=True)

        self.fields["book_name"].queryset = available_books

        if not available_books.exists():
            self.fields["book_name"].empty_label = "No books available"


class UpdateStatusForm(forms.ModelForm):

    class Meta:
        model = Booking
        fields = ["status"]

        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
        }


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaints
        fields = ["report_issue", "book_name"]

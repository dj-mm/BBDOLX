from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
from django.contrib.auth.password_validation import validate_password
import re

from .models import Product, Profile


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        label="Password"
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm password"
    )

    username = forms.CharField(
        max_length=150,
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z0-9_]{3,20}$',
                message="Username can contain letters, numbers and underscore only (3–20 characters)."
            )
        ]
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # ✅ EMAIL VALIDATION
    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        pattern = r'^[\w\.-]+@(bbdnitm\.ac\.in|bbdniit\.ac\.in|bbdu\.org)$'
        if not re.match(pattern, email):
            raise ValidationError(
                "Use your official college email (@bbdnitm.ac.in, @bbdniit.ac.in or @bbdu.org)."
            )

        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")

        return email

    # ✅ PASSWORD VALIDATION (MAIN FIX)
    def clean_password(self):
        password = self.cleaned_data.get('password')

        # Django built-in validators (length, common, similarity, numeric)
        validate_password(password)

        # Extra rule: must contain at least 1 letter & 1 digit
        if not re.search(r'[A-Za-z]', password):
            raise ValidationError("Password must contain at least one letter.")

        if not re.search(r'\d', password):
            raise ValidationError("Password must contain at least one number.")

        return password

    # ✅ CONFIRM PASSWORD MATCH
    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')

        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")

        return cleaned

from django import forms
from django.core.exceptions import ValidationError
from .models import Profile


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['phone', 'whatsapp', 'branch', 'year', 'hide_name']
        labels = {
            'phone': 'Phone number (optional)',
            'whatsapp': 'WhatsApp number for chat',
            'branch': 'Branch',
            'year': 'Year',
            'hide_name': 'Hide my name from buyers',
        }
        widgets = {
            'phone': forms.TextInput(attrs={
                'placeholder': 'e.g. 9876543210'
            }),
            'whatsapp': forms.TextInput(attrs={
                'placeholder': 'WhatsApp number used for chat'
            }),
            'branch': forms.TextInput(attrs={
                'placeholder': 'e.g. CSE, ECE, BBA...'
            }),
            'year': forms.TextInput(attrs={
                'placeholder': 'e.g. 1st, 2nd, 3rd, Final'
            }),
            'hide_name': forms.CheckboxInput(attrs={
                'class': 'h-4 w-4 text-teal-600'
            }),
        }

    # ✅ STEP 1: WhatsApp validation (REQUIRED)
    def clean_whatsapp(self):
        whatsapp = (self.cleaned_data.get('whatsapp') or '').strip()

        if not whatsapp:
            raise ValidationError(
                "WhatsApp number is required to post ads on CAMPUS-OLX."
            )

        if not whatsapp.isdigit():
            raise ValidationError(
                "WhatsApp number must contain digits only."
            )

        if len(whatsapp) != 10:
            raise ValidationError(
                "Enter a valid 10-digit WhatsApp number."
            )

        return whatsapp
    def clean_branch(self):
        branch = (self.cleaned_data.get('branch') or '').strip()

        if not branch:
            raise ValidationError("Branch is required.")

        if not re.match(r'^[A-Za-z ]+$', branch):
            raise ValidationError("Branch must contain letters only.")

        if len(branch) < 2:
            raise ValidationError("Enter a valid branch name.")

        return branch.upper()

    # ✅ Year validation
    def clean_year(self):
        year = (self.cleaned_data.get('year') or '').strip()

        allowed_years = ['1', '2', '3', '4', '1st', '2nd', '3rd', 'final']

        if not year:
            raise ValidationError("Year is required.")

        if year.lower() not in allowed_years:
            raise ValidationError(
                "Enter a valid year (1st, 2nd, 3rd, 4th or Final)."
            )

        return year.capitalize()
     # ✅ Phone number validation (OPTIONAL)
    def clean_phone(self):
        phone = (self.cleaned_data.get('phone') or '').strip()

        # Allow empty phone number
        if not phone:
            return phone

        if not phone.isdigit():
            raise ValidationError(
                "Phone number must contain digits only."
            )

        if len(phone) != 10:
            raise ValidationError(
                "Enter a valid 10-digit phone number."
            )

        return phone


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = [
            'title',
            'description',
            'category',
            'price',
            'condition',
            'image',
            'city_campus',
        ]

    def clean_image(self):
        image = self.cleaned_data.get("image")

        # 🔒 Approved ad → image cannot be changed
        if self.instance.pk and self.instance.status == "APPROVED":
            return self.instance.image

        if not image:
            raise ValidationError("Please upload an image.")

        max_size = 2 * 1024 * 1024  # 2 MB
        if image.size > max_size:
            raise ValidationError(
                "Image size is more than 2 MB. Please try again with a smaller image."
            )

        return image

    def clean(self):
        cleaned_data = super().clean()
        image = cleaned_data.get("image")

        # 🔁 Double safety (prevents silent bypass)
        if image and image.size > 2 * 1024 * 1024:
            self.add_error(
                "image",
                "Image size exceeds 2 MB. Please upload a smaller image."
            )

        return cleaned_data

    def clean_title(self):
        title = (self.cleaned_data.get('title') or '').strip()

        if len(title) < 4:
            raise ValidationError("Title should be at least 4 characters.")
        if len(title) > 200:
            raise ValidationError("Title is too long (max 200 characters).")

        # Very light check to avoid obviously weird input
        blocked_keywords = ['drop table', 'alter table', 'insert into', 'delete from', 'truncate ']
        lower = title.lower()
        if any(kw in lower for kw in blocked_keywords):
            raise ValidationError("Title contains invalid text.")

        return title

    def clean_description(self):
        desc = (self.cleaned_data.get('description') or '').strip()

        if len(desc) < 10:
            raise ValidationError("Please add a bit more detail to your description.")
        if len(desc) > 3000:
            raise ValidationError("Description is too long (max 3000 characters).")

        # same mild protection here
        blocked_keywords = ['drop table', 'alter table', 'insert into', 'delete from', 'truncate ']
        lower = desc.lower()
        if any(kw in lower for kw in blocked_keywords):
            raise ValidationError("Description contains invalid text.")

        return desc

    def clean_price(self):
        price = self.cleaned_data.get('price')

        if price is None:
            raise ValidationError("Price is required.")

        if price <= 0:
            raise ValidationError("Price must be greater than 0.")
        if price > 1000000:
            raise ValidationError("Price looks too high for campus market.")

        return price

    def clean_city_campus(self):
        city = (self.cleaned_data.get('city_campus') or '').strip()

        if len(city) == 0:
            raise ValidationError("City / campus is required.")
        if len(city) > 100:
            raise ValidationError("City / campus name is too long.")

        return city

    # ------- FORM-LEVEL VALIDATION (optional extra safety) -------

    def clean(self):
        data = super().clean()

        # You can centralise any extra cross-field validation here
        # but do NOT trust user input for raw SQL anywhere – always use Django ORM
        # (which you already do in your views, so you're safe 💪)

        return data

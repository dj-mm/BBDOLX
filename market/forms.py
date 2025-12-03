from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator

from .models import Product, Profile


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    # Optional: add a regex validator on username field itself
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

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()

        # Regex: normal email + only allowed domains
        import re
        pattern = r'^[\w\.-]+@(bbdnitm\.ac\.in|bbdniit\.ac\.in|bbdu\.org)$'
        if not re.match(pattern, email):
            raise ValidationError(
                "Use your official college email (@bbdnitm.ac.in, @bbdniit.ac.in or @bbdu.org)."
            )

        # Optional: block duplicate emails if needed
        if User.objects.filter(email=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password', '')

        # At least 8 chars, 1 letter, 1 digit
        import re
        pattern = r'^(?=.*[A-Za-z])(?=.*\d).{8,}$'
        if not re.match(pattern, password):
            raise ValidationError(
                "Password must be at least 8 characters and include at least one letter and one number."
            )
        return password

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned


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

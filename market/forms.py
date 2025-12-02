from django import forms
from django.contrib.auth.models import User
from .models import Product


class StudentRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-field',
            'id': 'password'
        })
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'password-field',
            'id': 'confirm_password'
        })
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def clean_email(self):
        email = self.cleaned_data.get('email')

        allowed_domains = [
            '@bbdnitm.ac.in',
            '@bbdniit.ac.in',
            '@bbdu.org',
        ]

        if not any(email.endswith(domain) for domain in allowed_domains):
            raise forms.ValidationError(
                "Only BBD email IDs are allowed: @bbdnitm.ac.in, @bbdniit.ac.in, @bbdu.org"
            )
        return email

    def clean(self):
        cleaned = super().clean()
        p1 = cleaned.get('password')
        p2 = cleaned.get('confirm_password')
        if p1 and p2 and p1 != p2:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned


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

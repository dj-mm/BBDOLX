from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Product actions
    path('product/add/', views.product_create, name='product_add'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('product/<int:pk>/sold/', views.mark_as_sold, name='product_sold'),

    # Seller dashboard
    path('my-listings/', views.my_listings, name='my_listings'),

    # Moderation (Admin/Staff Only)
    path('moderation/pending/', views.pending_products, name='pending_products'),
    path('moderation/approve/<int:pk>/', views.approve_product, name='approve_product'),
    path('moderation/reject/<int:pk>/', views.reject_product, name='reject_product'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),
    path('product/<int:pk>/sold/', views.mark_as_sold, name='product_sold'),
    path('product/<int:pk>/rate/', views.rate_product, name='rate_product'),
    path('moderation/approve/<int:pk>/', views.approve_product, name='approve_product'),
    path('moderation/pending/', views.pending_products, name='pending_products'),



]

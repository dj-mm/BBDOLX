from django.urls import path
from . import views

urlpatterns = [
    # ---------- PUBLIC PAGES ----------
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('campus-safety/', views.campus_safety, name='campus_safety'),
    path('contact/', views.contact, name='contact'),
    # ---------- SUPPORT PAGES ----------

path('privacy-policy/', views.privacy_policy, name='privacy_policy'),
path('terms-and-conditions/', views.terms_and_conditions, name='terms_and_conditions'),
path('development-team/', views.development_team, name='development_team'),



    path('register/', views.register, name='register'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('resend-otp/', views.resend_otp, name='resend_otp'),

    # ---------- PRODUCTS (USER) ----------
    path('product/add/', views.product_create, name='product_add'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:pk>/edit/', views.product_update, name='product_edit'),
    path('product/<int:pk>/sold/', views.mark_as_sold, name='product_sold'),

    # ---------- SELLER DASHBOARD ----------
    path('my-listings/', views.my_listings, name='my_listings'),
    path('product/<int:pk>/delete/', views.delete_my_product, name='product_delete'),


    # ---------- MODERATION (ADMIN / STAFF ONLY) ----------
    path('moderation/', views.moderation_dashboard, name='moderation_dashboard'),
    path('moderation/pending/', views.pending_products, name='pending_products'),
    path('moderation/approve/<int:pk>/', views.approve_product, name='approve_product'),
    path('moderation/reject/<int:pk>/', views.reject_product, name='reject_product'),
    path('moderation/<int:pk>/delete/', views.delete_product, name='delete_product'),

    # ---------- NOTIFICATIONS ----------
    path('notif/read/<int:pk>/', views.mark_notification_read, name='mark_notification_read'),

    # ---------- PROFILE ----------
    path('profile/', views.edit_profile, name='edit_profile'),
    path("accounts/profile/", views.profile_view, name="profile"),
]

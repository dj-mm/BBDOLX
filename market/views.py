from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings

import random
import requests

from .forms import StudentRegisterForm, ProductForm
from .models import Product, Category, EmailOTP, Notification


# ---------- HOME ----------

# ---------- HOME ----------

def home(request):
    query = request.GET.get('q', '')
    category_slug = request.GET.get('category', '')

    products = Product.objects.filter(
        is_sold=False,
        status='APPROVED'
    ).order_by('-created_at')

    if query:
        products = products.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(city_campus__icontains=query)
        )

    if category_slug:
        products = products.filter(category__slug=category_slug)

    categories = Category.objects.all()
    quick_categories = [
    ("📱", "Mobiles", "mobiles"),
    ("💻", "Laptops", "laptops"),
    ("🚲", "Bikes", "bikes"),
    ("🚗", "Cars", "cars"),
    ("📚", "Books", "books"),
    ("🛏️", "Hostel Essentials", "hostel-essentials"),
    ("🎧", "Electronics", "electronics"),
    ("👕", "Clothing", "clothing"),
    ("🏋️", "Fitness", "fitness"),
    ("🎮", "Gaming", "gaming"),
    ("🪑", "Furniture", "furniture"),
    ("🛒", "Others", "others"),
]


    context = {
        'products': products,
        'categories': categories,
        'query': query,
        'category_slug': category_slug,
        'quick_categories': quick_categories,

    }


    return render(request, 'market/home.html', context)


# ---------- OTP / AUTH ----------

# ---------- OTP / AUTH ----------

def send_otp_email(request, user):
    """Generate OTP, save it, and send via Google Apps Script."""
    otp = str(random.randint(100000, 999999))

    otp_obj, created = EmailOTP.objects.get_or_create(user=user)
    otp_obj.otp = otp
    otp_obj.created_at = timezone.now()
    otp_obj.save()

    payload = {
        "email": user.email,
        "otp": otp,
        "secret": settings.APPS_SCRIPT_OTP_SECRET,
    }

    try:
        # DEBUG logs – check these in the runserver terminal
        print("Sending OTP payload to Apps Script:", payload)
        resp = requests.post(settings.APPS_SCRIPT_OTP_URL, json=payload, timeout=10)
        print("Apps Script response:", resp.status_code, resp.text)

        if resp.status_code == 200:
            messages.success(request, "We sent an OTP to your email. It expires in 2 minutes.")
        else:
            messages.error(request, "Could not send OTP email (server error). Please try again.")
    except requests.RequestException as e:
        print("Error calling Apps Script:", e)  # DEBUG
        messages.error(request, "Could not connect to email service. Please try again later.")



def register(request):
    if request.method == 'POST':
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.is_active = False
            user.save()

            # send OTP via Apps Script
            send_otp_email(request, user)

            request.session['pending_user_id'] = user.id
            return redirect('verify_otp')
    else:
        form = StudentRegisterForm()

    return render(request, 'market/register.html', {'form': form})


def verify_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, "No pending verification found. Please register again.")
        return redirect('register')

    user = get_object_or_404(User, id=user_id)
    otp_obj = get_object_or_404(EmailOTP, user=user)

    if request.method == 'POST':
        entered = request.POST.get('otp', '').strip()

        # Check expiry (2 minutes, via model method)
        if otp_obj.is_expired():
            messages.error(request, "OTP expired. Sending a new one...")
            send_otp_email(request, user)
            return redirect('verify_otp')

        if entered == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            request.session.pop('pending_user_id', None)
            login(request, user)
            messages.success(request, "Email verified successfully. Welcome to BBDOLX!")
            return redirect('home')
        else:
            messages.error(request, "Incorrect OTP. Please try again.")

    return render(request, 'market/verify_otp.html')



@require_POST
def resend_otp(request):
    user_id = request.session.get('pending_user_id')
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect('register')

    user = get_object_or_404(User, id=user_id)
    send_otp_email(request, user)  # message is added inside this function
    return redirect('verify_otp')


# ---------- PRODUCTS ----------

@login_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.status = 'PENDING'   # waiting for admin approval
            product.save()
            return redirect('my_listings')
    else:
        form = ProductForm()
    return render(request, 'market/product_form.html', {
        'form': form,
        'title': 'Post an Ad'
    })


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'market/product_detail.html', {'product': product})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('product_detail', pk=product.pk)
    else:
        form = ProductForm(instance=product)
    return render(request, 'market/product_form.html', {
        'form': form,
        'title': 'Edit Ad'
    })


@login_required
@require_POST
def mark_as_sold(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    product.is_sold = True
    product.save()
    messages.success(request, "Listing marked as sold.")
    return redirect('my_listings')


@login_required
def my_listings(request):
    products = Product.objects.filter(owner=request.user).order_by('-created_at')
    return render(request, 'market/my_listings.html', {'products': products})


# ---------- MODERATION (staff only) ----------
# ---------- MODERATION HELPERS ----------
def staff_required(user):
    return user.is_staff  # Only staff/admin can access



@user_passes_test(staff_required)
@require_POST
def approve_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    product.status = 'APPROVED'
    product.rejection_reason = ''
    product.save()

    # Create notification for the owner
    Notification.objects.create(
        user=product.owner,
        message=f"Your ad '{product.title}' has been approved and is now live!"
    )

    messages.success(request, "Ad approved.")
    return redirect('pending_products')


@user_passes_test(staff_required)
def reject_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == 'POST':
        reason = request.POST.get('reason', '')

        product.status = 'REJECTED'
        product.rejection_reason = reason
        product.save()

        Notification.objects.create(
            user=product.owner,
            message=f"Your ad '{product.title}' was rejected. Reason: {reason}"
        )

        messages.error(request, "Ad rejected.")
        return redirect('pending_products')

    return render(request, 'market/reject_form.html', {'product': product})
from django.http import JsonResponse

@require_POST
@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({"status": "ok"})

@user_passes_test(staff_required)
def pending_products(request):
    products = Product.objects.filter(status='PENDING').order_by('-created_at')
    return render(request, 'market/pending_products.html', {'products': products})



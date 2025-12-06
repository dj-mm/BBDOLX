from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.views.decorators.http import require_POST
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth.models import User
from django.conf import settings
from django.http import JsonResponse

import random
import requests

from .forms import StudentRegisterForm, ProductForm, ProfileForm
from .models import Product, Category, EmailOTP, Notification, Profile


# ---------- HOME ----------

def home(request):
    query = request.GET.get("q", "")
    category_slug = request.GET.get("category", "")
    sort = request.GET.get("sort", "newest")

    # only active + approved listings on home
    products = Product.objects.filter(
        is_sold=False,
        status="APPROVED",
    )

    # search
    if query:
        products = products.filter(
            Q(title__icontains=query)
            | Q(description__icontains=query)
            | Q(city_campus__icontains=query)
        )

    # category filter
    if category_slug:
        products = products.filter(category__slug=category_slug)

    # sorting
    if sort == "low":
        products = products.order_by("price")
    elif sort == "high":
        products = products.order_by("-price")
    else:
        products = products.order_by("-created_at")  # newest first

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
        "products": products,
        "categories": categories,
        "query": query,
        "category_slug": category_slug,
        "quick_categories": quick_categories,
    }
    return render(request, "market/home.html", context)


# ---------- OTP / AUTH ----------

def send_otp_email(request, user):
    """Generate OTP, save it, and send via Google Apps Script."""
    otp = str(random.randint(100000, 999999))

    otp_obj, _ = EmailOTP.objects.get_or_create(user=user)
    otp_obj.otp = otp
    otp_obj.created_at = timezone.now()
    otp_obj.save()

    payload = {
        "email": user.email,
        "otp": otp,
        "secret": settings.APPS_SCRIPT_OTP_SECRET,
    }

    try:
        # DEBUG logs – visible in runserver / PythonAnywhere logs
        print("Sending OTP payload to Apps Script:", payload)
        resp = requests.post(settings.APPS_SCRIPT_OTP_URL, json=payload, timeout=10)
        print("Apps Script response:", resp.status_code, resp.text)

        if resp.status_code == 200:
            messages.success(request, "We sent an OTP to your email. It expires in 2 minutes.")
        else:
            messages.error(request, "Could not send OTP email (server error). Please try again.")
    except requests.RequestException as e:
        print("Error calling Apps Script:", e)
        messages.error(request, "Could not connect to email service. Please try again later.")


def register(request):
    if request.method == "POST":
        form = StudentRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.is_active = False
            user.save()

            # create/update Profile with WhatsApp from form
            whatsapp = form.cleaned_data.get("whatsapp", "")
            Profile.objects.update_or_create(
                user=user,
                defaults={"whatsapp": whatsapp},
            )

            send_otp_email(request, user)
            request.session["pending_user_id"] = user.id
            return redirect("verify_otp")
    else:
        form = StudentRegisterForm()

    return render(request, "market/register.html", {"form": form})


def verify_otp(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "No pending verification found. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)
    otp_obj = get_object_or_404(EmailOTP, user=user)

    if request.method == "POST":
        entered = request.POST.get("otp", "").strip()

        # Check expiry (2 minutes)
        if otp_obj.is_expired():
            messages.error(request, "OTP expired. Sending a new one...")
            send_otp_email(request, user)
            return redirect("verify_otp")

        if entered == otp_obj.otp:
            user.is_active = True
            user.save()
            otp_obj.delete()
            request.session.pop("pending_user_id", None)
            login(request, user)
            messages.success(request, "Email verified successfully. Welcome to BBDOLX!")
            return redirect("home")

        messages.error(request, "Incorrect OTP. Please try again.")

    return render(request, "market/verify_otp.html")


@require_POST
def resend_otp(request):
    user_id = request.session.get("pending_user_id")
    if not user_id:
        messages.error(request, "Session expired. Please register again.")
        return redirect("register")

    user = get_object_or_404(User, id=user_id)
    send_otp_email(request, user)
    return redirect("verify_otp")


# ---------- PRODUCTS (SELLER SIDE) ----------

@login_required
def product_create(request):
    # Ensure profile exists
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES)

        # Check WhatsApp first
        if not profile.whatsapp:
            messages.warning(
                request,
                "Please add your WhatsApp number in your profile before posting an ad.",
            )
            return redirect("profile")  # make sure this URL exists

        if form.is_valid():
            product = form.save(commit=False)
            product.owner = request.user
            product.status = "PENDING"  # waiting for admin approval

            # Optional usage checkboxes (from product_form.html)
            extra_info = []
            if request.POST.get("usage_light"):
                extra_info.append("• Lightly used (less than 6 months)")
            if request.POST.get("usage_long"):
                extra_info.append("• Used for a long time")

            if extra_info:
                base_desc = product.description or ""
                product.description = (base_desc.strip() + "\n\n" + "\n".join(extra_info)).strip()

            product.save()
            messages.success(request, "Your ad has been submitted for review.")
            return redirect("my_listings")
    else:
        form = ProductForm()

    return render(
        request,
        "market/product_form.html",
        {"form": form, "title": "Post an Ad"},
    )


def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, "market/product_detail.html", {"product": product})


@login_required
def product_update(request, pk):
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    if request.method == "POST":
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            # keep simple here; you can also re-apply usage checkboxes if you want
            form.save()
            messages.success(request, "Ad updated successfully.")
            return redirect("product_detail", pk=product.pk)
    else:
        form = ProductForm(instance=product)

    return render(
        request,
        "market/product_form.html",
        {"form": form, "title": "Edit Ad"},
    )


@login_required
@require_POST
def mark_as_sold(request, pk):
    """Seller marks their own product as sold."""
    product = get_object_or_404(Product, pk=pk, owner=request.user)
    product.is_sold = True
    product.status = "SOLD"
    product.save()
    messages.success(request, "Listing marked as sold.")
    return redirect("my_listings")


@login_required
def my_listings(request):
    products = Product.objects.filter(owner=request.user).order_by("-created_at")
    return render(request, "market/my_listings.html", {"products": products})


# ---------- PROFILE ----------

@login_required
def edit_profile(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("edit_profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "market/edit_profile.html", {"form": form})


@login_required
def profile_view(request):
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        form = ProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated successfully.")
            return redirect("profile")
    else:
        form = ProfileForm(instance=profile)

    return render(request, "market/profile.html", {"form": form})


# ---------- MODERATION (ADMIN / STAFF) ----------

def staff_required(user):
    return user.is_staff  # Only staff/admin can access


@user_passes_test(staff_required)
def moderation_dashboard(request):
    status_filter = request.GET.get("status", "PENDING")

    products = Product.objects.all().order_by("-created_at")
    if status_filter in ["PENDING", "APPROVED", "REJECTED", "SOLD"]:
        products = products.filter(status=status_filter)

    # Stats including SOLD
    stats_qs = Product.objects.values("status").annotate(total=Count("id"))
    stats = {"PENDING": 0, "APPROVED": 0, "REJECTED": 0, "SOLD": 0}
    for row in stats_qs:
        stats[row["status"]] = row["total"]

    context = {
        "products": products,
        "status_filter": status_filter,
        "stats": stats,
    }
    return render(request, "market/admin_dashboard.html", context)


@user_passes_test(staff_required)
@require_POST
def approve_product(request, pk):
    """
    Used for:
    - Pending  -> Approved
    - Rejected -> Approved
    - Sold     -> Active again (undo sold)
    """
    product = get_object_or_404(Product, pk=pk)
    product.status = "APPROVED"
    product.is_sold = False
    product.rejection_reason = ""
    product.save()

    Notification.objects.create(
        user=product.owner,
        message=f"Your ad '{product.title}' has been approved and is now live!",
    )

    messages.success(request, "Ad set to ACTIVE / APPROVED.")
    return redirect("moderation_dashboard")


@user_passes_test(staff_required)
def reject_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    if request.method == "POST":
        reason = request.POST.get("reason", "").strip()

        product.status = "REJECTED"
        product.rejection_reason = reason
        product.save()

        Notification.objects.create(
            user=product.owner,
            message=f"Your ad '{product.title}' was rejected. Reason: {reason or 'Not specified'}",
        )

        messages.error(request, "Ad rejected.")
        return redirect("moderation_dashboard")

    return render(request, "market/reject_form.html", {"product": product})


@user_passes_test(staff_required)
@require_POST
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk)

    Notification.objects.create(
        user=product.owner,
        message=f"Your ad '{product.title}' was removed by an admin.",
    )

    product.delete()
    messages.success(request, "Ad deleted permanently.")
    return redirect("moderation_dashboard")


# ---------- NOTIFICATIONS ----------

@require_POST
@login_required
def mark_notification_read(request, pk):
    notif = get_object_or_404(Notification, pk=pk, user=request.user)
    notif.is_read = True
    notif.save()
    return JsonResponse({"status": "ok"})


# Legacy URL – keeps old /moderation/pending/ working
@user_passes_test(staff_required)
def pending_products(request):
    return redirect("moderation_dashboard")

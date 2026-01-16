from .models import Notification, Profile

def notifications_processor(request):
    unread_notifications = []
    has_whatsapp = False

    if request.user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            user=request.user,
            is_read=False
        )

        # ✅ Always calculate WhatsApp state from DB (source of truth)
        profile = getattr(request.user, "profile", None)
        if profile and profile.whatsapp:
            has_whatsapp = True

    return {
        "unread_notifications": unread_notifications,
        "has_whatsapp": has_whatsapp,
    }

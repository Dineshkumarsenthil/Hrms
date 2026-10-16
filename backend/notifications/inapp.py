"""In-app notifications. Emails stay in service.py; this file only writes Notification rows."""
from django.contrib.auth import get_user_model
from django.db import transaction

from .models import Broadcast, Notification, NotificationPreference

User = get_user_model()


def _muted_user_ids(kind):
    return set(NotificationPreference.objects.filter(kind=kind, enabled=False).values_list("user_id", flat=True))


def notify(user, kind, title, message, link="", broadcast=None):
    """Create one notification unless the user switched this kind off. Never raises."""
    if user is None:
        return None
    try:
        if NotificationPreference.objects.filter(user=user, kind=kind, enabled=False).exists():
            return None
        return Notification.objects.create(user=user, kind=kind, title=title[:120], message=message[:1000], link=link, broadcast=broadcast)
    except Exception:  # a notification problem must never break the business action
        return None


def notify_many(users, kind, title, message, link="", broadcast=None):
    """Same as notify() for a list of users, with a single INSERT. Returns how many were created."""
    muted = _muted_user_ids(kind)
    rows = [Notification(user=u, kind=kind, title=title[:120], message=message[:1000], link=link, broadcast=broadcast) for u in users if u.id not in muted]
    Notification.objects.bulk_create(rows)
    return len(rows)


def notify_staff(kind, title, message, link="", exclude_user=None):
    """Tell every active Admin and HR user."""
    staff = User.objects.filter(role__in=["ADMIN", "HR"], is_active=True)
    if exclude_user is not None:
        staff = staff.exclude(pk=exclude_user.pk)
    return notify_many(list(staff), kind, title, message, link)


@transaction.atomic
def send_broadcast(sender, title, message, department=None):
    users = User.objects.filter(is_active=True)
    if department:
        users = users.filter(employee__department=department)
    b = Broadcast.objects.create(title=title, message=message, department=department, sent_by=sender)
    b.recipient_count = notify_many(list(users), Notification.Kind.ANNOUNCEMENT, title, message, "/notifications", broadcast=b)
    b.save(update_fields=["recipient_count"])
    return b

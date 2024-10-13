from users.models import Notification


def create_notification(username, notification):
    Notification.objects.create(username=username, notification=notification)

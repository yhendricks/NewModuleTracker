from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.dispatch import receiver

@receiver(post_delete, sender=User)
def promote_last_user_to_superuser(sender, instance, **kwargs):
    """
    Promotes the last remaining user to superuser when others are deleted
    """
    remaining_users = User.objects.count()
    if remaining_users == 1:
        last_user = User.objects.first()
        if not last_user.is_superuser:
            last_user.is_superuser = True
            last_user.is_staff = True
            last_user.save()
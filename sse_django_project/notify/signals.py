from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import User
import redis, json
from core.redis_client import get_redis_connection

@receiver(post_save, sender=User)
def broadcast_staff_status(sender, instance, **kwargs):
    print('signal broadcast staff_status')
    if instance.user_type == 'staff' and instance.organization_id:
        org_channel = f"org_{instance.organization_id}_updates"

        redis_conn = get_redis_connection()

        staff_list = list(
            instance.organization.get_staff_list()
        )
        online_count = instance.organization.get_staff_count()

        data = {
            'online_count': online_count,
            'staff_list': staff_list,
            'timestamp': timezone.now().isoformat(),
        }

        print('data', data)

        redis_conn.publish(org_channel, json.dumps(data))
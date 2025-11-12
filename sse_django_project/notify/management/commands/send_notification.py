from django.core.management.base import BaseCommand
from asgiref.sync import async_to_sync
from notify.sse import send_message

class Command(BaseCommand):
    help = "Send a notification to all SSE clients"

    def add_arguments(self, parser):
        parser.add_argument('message', type=str)

    def handle(self, *args, **options):
        message = options['message']
        async_to_sync(send_message)(message)
        self.stdout.write(self.style.SUCCESS(f"Sent: {message}"))

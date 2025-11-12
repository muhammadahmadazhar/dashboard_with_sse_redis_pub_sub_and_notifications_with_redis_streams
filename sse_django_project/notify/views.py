import asyncio
from django.http import StreamingHttpResponse
from .sse import event_stream

# async def sse_view(request):
#     response = StreamingHttpResponse(
#         event_stream(),
#         content_type='text/event-stream',
#     )
#     response['Cache-Control'] = 'no-cache'
#     return response
#
# # async def sse_view(request):
# #     async def generator():
# #         for i in range(5):
# #             yield f"data: test message {i}\n\n"
# #             await asyncio.sleep(1)
# #     response = StreamingHttpResponse(generator(), content_type='text/event-stream')
# #     response['Cache-Control'] = 'no-cache'
# #     return response


import json
import time
from django.http import StreamingHttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import User, Organization

# # In-memory storage for SSE connections (in production, use Redis)
# sse_connections = {}
#
#
# def event_stream(user):
#     """Generator function for SSE"""
#     # Store connection
#     connection_id = f"{user.id}_{time.time()}"
#
#     while True:
#         try:
#             if user.user_type == 'admin' and user.organization:
#                 # Get staff data for this admin's organization
#                 staff_users = list(user.organization.get_staff_list())
#                 online_count = user.organization.get_staff_count()
#
#                 data = {
#                     'online_count': online_count,
#                     'staff_list': staff_users,
#                     'timestamp': timezone.now().isoformat()
#                 }
#
#                 yield f"data: {json.dumps(data)}\n\n"
#
#             time.sleep(2)  # Send update every 2 seconds
#
#         except GeneratorExit:
#             break
#         except Exception as e:
#             print(f"SSE Error: {e}")
#             break

import json
import asyncio
import redis.asyncio as aioredis
from django.http import StreamingHttpResponse, JsonResponse
from django.conf import settings
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async


async def event_stream(user, org_id):
    """Async generator that listens to Redis Pub/Sub for organization updates."""
    redis_conn = aioredis.from_url(settings.REDIS_URL, decode_responses=True)
    pubsub = redis_conn.pubsub()
    org_channel = f"org_{org_id}_updates"
    await pubsub.subscribe(org_channel)

    print('aa')

    try:
        async for message in pubsub.listen():
            if message["type"] == "message":
                payload = json.loads(message["data"])
                yield f"data: {json.dumps(payload)}\n\n"
    except asyncio.CancelledError:
        # Happens when the browser disconnects
        await pubsub.unsubscribe(org_channel)
        await pubsub.close()
        raise
    finally:
        await redis_conn.close()


@login_required
async def staff_status_stream(request):
    """SSE endpoint for real-time staff status updates."""
    user = await sync_to_async(lambda: request.user)()
    org_id = await sync_to_async(lambda: user.organization_id)()
    # if user.user_type != 'admin':
    #     return JsonResponse({'error': 'Only admins can access this endpoint'}, status=403)

    response = StreamingHttpResponse(
        event_stream(user, org_id),
        content_type='text/event-stream'
    )
    response['Cache-Control'] = 'no-cache'
    response['X-Accel-Buffering'] = 'no'
    response['Connection'] = 'keep-alive'
    return response


@login_required
def get_staff_status(request):
    """Get current staff status (non-SSE endpoint)"""
    if request.user.user_type != 'admin':
        return JsonResponse({'error': 'Only admins can access this endpoint'}, status=403)

    if not request.user.organization:
        return JsonResponse({'error': 'No organization assigned'}, status=400)

    staff_users = list(request.user.organization.get_staff_list())
    online_count = request.user.organization.get_staff_count()

    return JsonResponse({
        'online_count': online_count,
        'staff_list': staff_users,
        'organization': request.user.organization.name
    })


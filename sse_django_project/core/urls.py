"""
URL configuration for core project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.urls import path
# from notify.views import sse_view
from notify import views
from django.http import HttpResponse

def index(request):
    return HttpResponse("""
    <html>
    <body>
      <h2>Live Notifications</h2>
      <div id="messages"></div>
      <script>
        const evtSource = new EventSource('/sse/');
        evtSource.onmessage = function(event) {
            const div = document.getElementById('messages');
            div.innerHTML += '<p>' + event.data + '</p>';
        };
      </script>
    </body>
    </html>
    """)


urlpatterns = [
    path('admin/', admin.site.urls),
    # path('', index),
    # path('sse/', sse_view),

    # SSE endpoint for real-time updates
    path('api/staff-status/stream/', views.staff_status_stream, name='staff_status_stream'),

    # REST endpoints
    path('api/staff-status/', views.get_staff_status, name='get_staff_status'),
]

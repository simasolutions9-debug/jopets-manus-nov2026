from django.urls import re_path
from .consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<tenant_id>[0-9a-f-]+)/(?P<peer_id>[0-9]+)/$", ChatConsumer.as_asgi()),
]

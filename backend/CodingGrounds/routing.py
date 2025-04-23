from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/session/(?P<session_id>[^/]+)/$', consumers.SessionConsumer.as_asgi()),
    # re_path(r'ws/echo/$', consumers.EchoConsumer.as_asgi()),
    re_path(r'ws/test/(?P<session_id>\w+)/$', consumers.SimpleTestConsumer.as_asgi()),

]
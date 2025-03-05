from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/sessions/(?P<session_id>[\w-]+)/$', consumers.GameSessionConsumer.as_asgi()),
    # re_path(r'ws/echo/$', consumers.EchoConsumer.as_asgi()),
    re_path(r'ws/test/(?P<session_id>\w+)/$', consumers.SimpleTestConsumer.as_asgi()),

]
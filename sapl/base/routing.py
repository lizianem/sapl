from django.conf.urls import url

from . import consumers

websocket_urlpatterns = [
    url(r'^ws/chat/(?P<room_name>[^/]+)/$', consumers.ChatConsumer),

    url(r'^ws/time-refresh/$', consumers.TimeRefreshConsumer),

    url(r'^ws/painel-principal/(?P<pk>\d+)/$', consumers.PainelConsumer),
]

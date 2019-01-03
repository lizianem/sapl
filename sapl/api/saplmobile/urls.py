from django.conf.urls import url, include
from rest_framework.routers import SimpleRouter
from sapl.api.saplmobile.views import TimeRefreshDatabaseView, TimeRefreshSetViews


# Não adicione app_name
# app_name = AppConfig.name

router = SimpleRouter()
for app, built_sets in TimeRefreshSetViews.items():
    for view_prefix, viewset in built_sets.items():
        router.register(app + '/' + view_prefix, viewset)


urlpatterns_router = router.urls

urlpatterns_sapl_mobile = [
    url(r'time_refresh$',
        TimeRefreshDatabaseView.as_view(), name="time_refresh"),
]

urlpatterns = [
    url(r'^mobile/', include(urlpatterns_sapl_mobile)),
    url(r'^mobile/', include(urlpatterns_router)),
]

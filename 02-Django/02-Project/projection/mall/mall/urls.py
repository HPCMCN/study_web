from utils.tools import auto_append_url

urlpatterns = auto_append_url("apps")
# from django.conf.urls import url, include
# from django.contrib import admin
# urlpatterns = [
#         url(r'^admin/', admin.site.urls),
#         url(r"^areas/", include("areas.urls")),
#         url(r"^users/", include("users.urls")),
#         url(r"^verifications/", include("verifications.urls")),
#         url(r"^oauth/", include("oauth.urls")),
#     ]
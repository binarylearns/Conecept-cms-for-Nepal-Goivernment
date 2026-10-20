
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('newsportalapp.urls')),
    path("dashboard/", include("mgntdashboard.urls")),
    path("adashboard/", include("authorapp.urls")),
]

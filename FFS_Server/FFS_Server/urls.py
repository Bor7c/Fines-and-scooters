"""
URL configuration for FFS_Server project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
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
from FFS.views.FinesViews import *
from FFS.views.BreachesViews import *
from FFS.views.CoFViews import *
from FFS.views.UsersViews import *


from rest_framework import permissions
from django.urls import path, include


from drf_yasg.views import get_schema_view # type: ignore
from drf_yasg import openapi # type: ignore

from rest_framework import routers

router = routers.DefaultRouter()

schema_view = get_schema_view(
    openapi.Info(
        title="Snippets API",
        default_version='v1',
        description="Test description",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="contact@snippets.local"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)

# router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('accounts/login/', login_view),
    path('accounts/logout/', logout_view),
    path('accounts/check/', check),

    path(r'fines/', fines),
    path(r'fines/search/', search_fines),
    path(r'fines/<int:fine_id>/', get_fine),
    path(r'fines/<int:fine_id>/add_to_breach/', add_fine_to_breach),
    path(r'fines/<int:fine_id>/edit/', edit_fine),
    path(r'fines/add/', add_fine),

    path(r'breaches/', search_breaches),
    path(r'breaches/<int:breach_id>/', get_breach),
    path(r'breaches/<int:breach_id>/delete/', delete_breach),
    path(r'breaches/<int:breach_id>/name/', update_breach_name),
    path(r'breaches/<int:breach_id>/delete_fine/<int:fine_id>/', delete_fine_from_breach),
    path(r'breaches/update_status_user/', update_breach_status_user),
    path(r'breaches/<int:breach_id>/update_status_admin/', update_breach_status_admin),
]

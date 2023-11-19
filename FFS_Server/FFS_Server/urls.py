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


from drf_yasg.views import get_schema_view
from drf_yasg import openapi

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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),

    path('accounts/login/', login_view, name='login'),
    path('accounts/logout/', logout_view, name='logout'),

    path(r'fines/', fines_action, name='fines-list'),
    path(r'fines/<int:pk>/', fine_action, name='fine-action'),

    path(r'breaches/', breaches_action, name='breaches-list'),
    path(r'breaches/<int:pk>/', breach_action, name='breach-action'),
    path(r'breaches/<int:pk>/end/', breach_final, name='breach-final'),

    path(r'cof/<int:pk>/', Change_Fine, name='cof-action'),

]

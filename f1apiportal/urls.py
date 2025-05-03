"""
URL configuration for f1apiportal project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from apiportal import views


from django.urls import path
from apiportal import views

urlpatterns = [
    path("", views.index, name="index"),
    path("client_scopes/", views.client_scopes, name="client_scopes"),
    path("client_scopes/edit/", views.client_scopes_edit, name="client_scopes_edit"),
    path(
        "client_scopes/<str:client_id>/",
        views.client_scopes_detail,
        name="client_scopes_detail",
    ),
    path(
        "client_scopes_edit_success/",
        views.client_scopes_edit_success,
        name="client_scopes_edit_success",
    ),
    path("new_client/", views.new_client, name="new_client"),
    path("new_client/success/", views.new_client_success, name="new_client_success"),
]

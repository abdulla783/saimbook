"""saimbook URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import path, include
from social import views

app_name = "social"

urlpatterns = [
    path('post_create/', views.post_create, name='post_create'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('my_profile/', views.my_profile, name='my_profile'),
    path('my_post/', views.my_post, name='my_post'),
    path('favourite/', views.post_favourite_list, name='post_favourite_list'),
    path('<int:id>/post_delete/', views.post_delete, name='post_delete'),
    path('<int:id>/favourite_post/', views.favourite_post, name='favourite_post'),
    path('<int:id>/post_edit/', views.post_edit, name='post_edit'),
    path('<int:id>/<str:slug>/', views.post_detail, name='post_detail'),
]

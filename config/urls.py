"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls.py import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls.py'))
"""

from django.contrib import admin
from django.urls import path, include
from .swagger_view import *
admin.AdminSite.site_header = 'Mindpairing'
admin.AdminSite.site_title = '관리자 모드'

urlpatterns = [
    path('swagger/', swagger_view, name='swagger'),
    path('admin/', admin.site.urls, name='admin'),
    path('users/', include('membership.urls'), name='users'),
    path('boards/', include('board.urls'), name='board'),
    path('mbti/', include('mbti.urls'), name='mbti'),
]

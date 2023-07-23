from django.contrib import admin
from .models import *
from mbti.models import *


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['id', 'is_init', 'nickname', 'gender', 'mbti']
    readonly_fields = ['password', ]
    list_display_links = ['nickname']
    search_fields = ['nickname', ]
    ordering = ['-id']


@admin.register(OpenAuth)
class OpenAuthAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'kakao_update_at', 'naver_update_at', 'google_update_at', 'apple_update_at']
    search_fields = ['user_id__nickname']
    ordering = ['-id']

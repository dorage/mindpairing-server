from django.contrib import admin
from .models import *


@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    # form = HashtagAdminForm
    list_display = ['text', 'ref_count']
    list_display_links = ['text', 'ref_count']
    search_fields = ['text', ]
    ordering = ['-ref_count', ]
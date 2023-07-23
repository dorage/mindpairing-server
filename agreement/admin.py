from django.contrib import admin
from .models import *

admin.site.register(Terms)


class AgreementAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'terms_id', 'agreement']
    search_fields = ['user_id']


admin.site.register(Agreement, AgreementAdmin)


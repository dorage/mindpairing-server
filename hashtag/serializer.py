from rest_framework import serializers
from .models import *


class HashtagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hashtag
        fields = ('content', 'ref_count')

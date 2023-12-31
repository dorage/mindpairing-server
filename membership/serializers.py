from rest_framework import serializers
from .models import *


class UserProfileSerializer(serializers.ModelSerializer):
    # formatted_create_at = serializers.DateTimeField()

    class Meta:
        model = User
        fields = ('nickname', 'name', 'gender', 'phone', 'email', 'image', 'mbti', 'create_at')


class UserSimpleProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('nickname', 'mbti', 'image')

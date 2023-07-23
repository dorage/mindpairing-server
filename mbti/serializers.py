from rest_framework import serializers
from .models import *


class MBTIQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIQuestion
        fields = ('index', 'text')


class MBTIClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIClass
        fields = ('mbti', 'title', 'summary', 'content')

from rest_framework import serializers
from .models import *


class MBTIQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = MBTIQuestion
        fields = ('index', 'text')


class MBTIClassSerializer(serializers.ModelSerializer):
    image = serializers.ImageField(use_url=True)

    def get_matches(self, mbti_class: MBTIClass):
        return [mbti_class.match[:4].upper(), mbti_class.match[4:].upper()]

    matches = serializers.SerializerMethodField(source=get_matches)

    class Meta:
        model = MBTIClass
        fields = ('mbti', 'title', 'summary', 'description', 'love', 'advice', 'matches', 'image')

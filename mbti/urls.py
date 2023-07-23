from django.urls import path
from .views import *

urlpatterns = [
    path('questions', MBTIQuestionList.as_view(), name='mbti_question'),  # get
    path('test', MBTITest.as_view(), name='mbti_test'),  # post
    path('result', MBTIResult.as_view(), name='mbti_result'),  # post
]
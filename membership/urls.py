from django.urls import path
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView
from mbti.views import *
from .views import *
from board.views import *

# /users/
urlpatterns = [
    path('login/kakao/', KakaoLoginAuth.as_view(), name='kakao_auth'),
    path('login/kakao/web/', KakaoLoginWeb.as_view(), name='kakao_web_login'),
    path('login/kakao/web/callback/', KakaoLoginWebCallback.as_view(), name='kakao_web_callback'),

    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('profile/', UserProfile.as_view(), name='profile'),  # GET, POST
]
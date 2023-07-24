from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.views import APIView
import requests
from .serializers import *
from django.conf import settings

KAKAO_OAUTH_URI = "https://kauth.kakao.com/oauth/authorize?response_type=code"
KAKAO_OAUTH_TOKEN_API = "https://kauth.kakao.com/oauth/token"
KAKAO_OAUTH_CLIENT_ID = settings.KAKAO_OAUTH_CLIENT_ID
KAKAO_OAUTH_REDIRECT_URI = settings.KAKAO_OAUTH_REDIRECT_URI

class KakaoLoginAuth(APIView):
    @swagger_auto_schema(
        tags=['로그인'],
        operation_id='kakao_login_auth_post',
        operation_summary='카카오 로그인',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'access_token': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='Kakao access token. Key is authorize-access-token in Cookie',
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description='서비스 이용 토큰 반환과 유저 정보 반환',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                        'is_init': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'access_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'refresh_token': openapi.Schema(type=openapi.TYPE_STRING),
                        'create_at': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description='Invalid access_token',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'msg': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                )
            ),
        }
    )
    def post(self, request):
        """
        Get access token
        """

        if 'access_token' not in request.data:
            return Response({'msg': 'request body NOT include \'access_token\''}, status=status.HTTP_400_BAD_REQUEST)

        me_url = "https://kapi.kakao.com/v2/user/me"
        res = requests.get(me_url, headers={
            "Authorization": f"Bearer {request.data['access_token']}"})

        if res.status_code != 200:
            return Response({'msg': 'request body should be in \'access_token\''}, status=status.HTTP_400_BAD_REQUEST)

        kakao_resource = res.json()  # {'id': <int>, 'connected_at': '2023-05-01T08:21:33Z', 'properties': {'nickname': '이강현'}, 'kakao_account': {'profile_nickname_needs_agreement': False, 'profile': {'nickname': '이강현'}}}
        print(kakao_resource)

        kakao_id = kakao_resource.get('id', None)
        if not kakao_id:
            return Response({'msg': 'Invalid kakao access_token'}, status=status.HTTP_400_BAD_REQUEST)

        oa, oa_created = OpenAuth.objects.get_or_create(kakao=f'k{kakao_id}')

        if oa_created:
            user = User.objects.create_user(nickname=f'k{kakao_id}')
            user_interest = UserInterest.objects.create(user_id=user)

            oa.user_id = user
            oa.kakao_update_at = timezone.now()
            user_interest.save()
            user.save()
            oa.save()
        else:
            user = oa.user_id

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        return Response({
            "nickname": user.nickname,
            "mbti": user.mbti,
            "is_init": user.is_init,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, status=status.HTTP_200_OK)


class KakaoLoginWeb(APIView):

    @swagger_auto_schema(
        operation_summary='For Server test only'
    )
    def get(self, request):
        uri = f"{KAKAO_OAUTH_URI}&client_id={KAKAO_OAUTH_CLIENT_ID}&redirect_uri={KAKAO_OAUTH_REDIRECT_URI}"
        return redirect(uri)


class KakaoLoginWebCallback(APIView):
    @swagger_auto_schema(
        operation_summary='For Server test only'
    )
    def get(self, request):
        data = {
            "grant_type": "authorization_code",
            "client_id": settings.KAKAO_OAUTH_CLIENT_ID,
            "redirection_uri": settings.KAKAO_OAUTH_REDIRECT_URI,
            "code": request.GET["code"],
        }

        # token_info = requests.post(KAKAO_OAUTH_TOKEN_API, data=data, headers={"Content-Type" : "application/json"}).json()
        token_info = requests.post(KAKAO_OAUTH_TOKEN_API, data=data, headers={"Content-Type" : "application/x-www-form-urlencoded"}).json()

        access_token = token_info["access_token"]
        kakao_resource = requests.get("https://kapi.kakao.com/v2/user/me", headers={
            "Authorization": f"Bearer {access_token}"}).json()

        oa, oa_created = OpenAuth.objects.get_or_create(kakao=kakao_resource['id'])

        if oa_created:
            user = User.objects.create_user(nickname=f"k{kakao_resource['id']}")

            oa.user_id = user
            oa.kakao_update_at = timezone.now()
            user.save()
            oa.save()
        else:
            user = oa.user_id

        token = TokenObtainPairSerializer.get_token(user)
        refresh_token = str(token)
        access_token = str(token.access_token)

        return Response({
            "nickname": user.nickname,
            "mbti": user.mbti,
            "is_init": user.is_init,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }, status=status.HTTP_200_OK)


class UserProfile(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [JWTAuthentication, ]

    @swagger_auto_schema(
        tags=['회원 정보'],
        operation_id='user_profile_get',
        operation_summary='내 정보 얻기',
        manual_parameters=[
        ],
        responses={
            200: openapi.Response(
                description='유저 정보',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                        'image': openapi.Schema(type=openapi.TYPE_STRING),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'email': openapi.Schema(type=openapi.TYPE_STRING),
                        'phone': openapi.Schema(type=openapi.TYPE_STRING),
                        'gender': openapi.Schema(type=openapi.TYPE_STRING),
                        'create_at': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description='Invalid access_token',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'msg': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                )
            ),
        }
    )
    def get(self, request):
        user_id: User = request.user
        serializer = UserProfileSerializer(User.objects.get(nickname=user_id.nickname), many=False)
        user_interest = UserInterest.objects.get(user_id=user_id)
        interest_mbtis = user_interest.mbtis.values_list('mbti', flat=True)
        interests = user_interest.interests.values_list('text', flat=True)
        return Response(data={**serializer.data, 'interest_mbtis': interest_mbtis, 'interests': interests}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['회원 정보'],
        operation_id='user_profile_post',
        operation_summary='내 정보 수정',
        request_body=openapi.Schema(
            description="변경 할 데이터를 body 에 포함하여 전송할 경우 해당 필드의 정보만 수정 됨",
            type=openapi.TYPE_OBJECT,
            properties={
                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                'mbti': openapi.Schema(type=openapi.TYPE_STRING, description='문자 [iesntfpj]만 허용. 소문자는 서버에서 upper 처리 됨'),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'gender': openapi.Schema(type=openapi.TYPE_STRING, description='한글자 [남여]만 허용'),
            },
        ),
        responses={
            200: openapi.Response(
                description='서비스 이용 토큰 반환과 유저 정보 반환',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                ),
            ),
            400: openapi.Response(
                description='Invalid access_token',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'msg': openapi.Schema(type=openapi.TYPE_STRING),
                    },
                )
            ),
        }
    )
    def post(self, request):
        user: User = request.user
        update_flag = False

        try:
            # if timezone.now() - user.update_at > django.utils.timezone.timedelta(=120):
            # if timezone.now().day == 16:
            user.nickname = request.data['nickname']
            update_flag = True
            user.is_init = True

        except Exception as e:
            pass

        try:
            user.phone = request.data['phone']
            update_flag = True
        except Exception as e:
            pass

        try:
            user.email = request.data['email']
            update_flag = True
        except Exception as e:
            pass

        try:
            user.name = request.data['name']
            update_flag = True
        except Exception as e:
            pass

        try:
            user.gender = int(request.data['gender'])
            update_flag = True
        except Exception as e:
            pass

        # try:
        #     user.image = request.data['image']
        #     update_flag = True
        # except Exception as e:
        #     pass

        try:
            user.mbti = request.data['mbti']
            update_flag = True
        except Exception as e:
            pass

        try:
            user_interest = UserInterest.objects.get(user_id=user)

            interest_mbtis = request.data['interest_mbtis']

            user_interest.mbtis.clear()
            for mbti in interest_mbtis:
                mbti_class = MBTIClass.objects.get(mbit=mbti)
                user_interest.mbtis.add(mbti_class)

            user_interest.save()
            update_flag = True
        except Exception as e:
            pass

        try:
            user_interest = UserInterest.objects.get(user_id=user)

            interests_list = request.data['interests']

            user_interest.interests.clear()
            for interest in interests_list:
                hashtag = Hashtag.objects.get_or_create(text=interest)
                user_interest.interests.add(hashtag)

            user_interest.save()
            update_flag = True
        except Exception as e:
            pass

        if update_flag:
            user.update_at = timezone.now()

        user.save()

        return Response({}, status=status.HTTP_200_OK)

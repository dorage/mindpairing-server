from typing import List

from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from mbti.serializers import *
from membership.models import User


def _MBTITest(answers: List[int]):
    questions = MBTIQuestion.objects.all()

    if len(answers) != len(questions):
        raise Exception('Number of \'answers\' NOT match')

    score = {'energy': 0, 'decision': 0, 'information': 0, 'lifestyle': 0, }
    max_score = {'energy': 0, 'decision': 0, 'information': 0, 'lifestyle': 0, }
    for q, a in zip(questions, answers):
        score[q.category] += getattr(q, f"select{a}_score")
        max_score[q.category] += max(q.select0_score, q.select3_score)

    threshold = MBTITestThreshold.objects.first()

    mbti = []

    mbti.append('I') if score['energy'] < threshold.energy else mbti.append('E')
    mbti.append('S') if score['information'] < threshold.information else mbti.append('N')
    mbti.append('T') if score['decision'] < threshold.decision else mbti.append('F')
    mbti.append('P') if score['lifestyle'] < threshold.lifestyle else mbti.append('J')

    result = {
        'score': {
            'energy': f"{score['energy']},{threshold.energy},{max_score['energy']}",
            'information': f"{score['information']},{threshold.information},{max_score['information']}",
            'decision': f"{score['decision']},{threshold.decision},{max_score['decision']}",
            'lifestyle': f"{score['lifestyle']},{threshold.lifestyle},{max_score['lifestyle']}",
        },
        'mbti': ''.join(mbti),
    }

    return result


class UserMBTI(APIView):
    permission_classes = [IsAuthenticated, ]
    authentication_classes = [JWTAuthentication, ]

    def get(self, request, nickname):
        try:
            if nickname == 'me':
                user = request.user
            else:
                user = User.objects.get(nickname=nickname)

            return Response({'nickname': user.nickname, 'mbti': user.mbti}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({}, status=status.HTTP_204_NO_CONTENT)

    def put(self, request, nickname):
        if nickname != 'me':
            return Response({}, status=status.HTTP_400_BAD_REQUEST)


        user = request.uest
        user.mbti = request.data['mbti']
        user.save()

        return Response({}, status=status.HTTP_200_OK)


class MBTITest(APIView):
    @swagger_auto_schema(
        tags=['MBTI 테스트'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['answers'],
            properties={
                'answers': openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_NUMBER
                    )
                )
            },
        ),
        manual_parameters=[

        ]
    )
    def post(self, request):
        """
        MBTI Test API

        MBTI 테스트 결과를 반환
        '0: 전혀 아님, 1: 아님, 2: 그렇다, 3: 매우 그렇다'
        """
        try:
            answers = request.data['answers']
            result = _MBTITest(answers)

            return Response({'data': result}, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)


class MBTIQuestionList(APIView):
    @swagger_auto_schema(
        tags=['MBTI 테스트'],
        operation_summary='',
        responses={
            200: openapi.Response(
                description='호출 성공',
                schema=openapi.Schema(type='Board')
            )
        }
    )
    def get(self, request):
        """
        MBTI 시험 질문 목록

        MBTI 시험 질문을 반환하는 API
        """
        serializer = MBTIQuestionSerializer(MBTIQuestion.objects.all(), many=True)
        return Response({'data': {'questions': serializer.data}}, status=status.HTTP_200_OK)


class MBTIResult(APIView):
    @swagger_auto_schema(
        tags=['MBTI 테스트'],
        manual_parameters=[
            openapi.Parameter('mbti', openapi.IN_QUERY, description="MBTI character", required=True, type=openapi.TYPE_STRING),
            openapi.Parameter('energy', openapi.IN_QUERY, description="SCORE,THRESHOLD,MAX_SCORE", type=openapi.TYPE_STRING),
            openapi.Parameter('information', openapi.IN_QUERY, description="SCORE,THRESHOLD,MAX_SCORE", type=openapi.TYPE_STRING),
            openapi.Parameter('decision', openapi.IN_QUERY, description="SCORE,THRESHOLD,MAX_SCORE", type=openapi.TYPE_STRING),
            openapi.Parameter('lifestyle', openapi.IN_QUERY, description="SCORE,THRESHOLD,MAX_SCORE", type=openapi.TYPE_STRING),
        ],
    )
    def get(self, request):
        """
        MBTI 유형 정보를 보여주는 API

        Parameter는 각 항목의 "점수,경계값,최대값"을 받는다.

        파라미터 예시
        mbti=INTP
        energy=4,9,20
        information=15,11,20
        decision=8,14,24
        lifestyle=3,8,16

        파라미터 값은 MBTI Test를 통해 얻을 수 있다
        """
        energy = request.GET.get('energy', None)
        information = request.GET.get('information', None)
        decision = request.GET.get('decision', None)
        lifestyle = request.GET.get('lifestyle', None)
        mbti = request.GET.get('mbti', 'XXXX')

        try:
            mbti_class = MBTIClass.objects.get(mbti=mbti)
            serializer = MBTIClassSerializer(mbti_class)
            return Response({
                'data': {
                    **serializer.data,
                    'score': {
                        'energy': energy,
                        'information': information,
                        'decision': decision,
                        'lifestyle': lifestyle,
                    },
                },
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

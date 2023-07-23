from django.core.paginator import Paginator
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .serializers import *

import re
import logging
logger = logging.getLogger("django")


class BoardList(APIView):
    @swagger_auto_schema(
        tags=['게시판'],
        operation_summary='게시판 분류 얻기',
        operation_id='board_list_get',
        operation_description='게시판 분류',
        responses={
            200: openapi.Response(
                description='게시판 분류와 분류 내 주제',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'data': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'index': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'category': openapi.Schema(type=openapi.TYPE_STRING),
                                    'topics': openapi.Schema(
                                        type=openapi.TYPE_ARRAY,
                                        items=openapi.Items(
                                            type=openapi.TYPE_OBJECT,
                                            properties={
                                                'index': openapi.Schema(type=openapi.TYPE_NUMBER),
                                                'topic': openapi.Schema(type=openapi.TYPE_STRING),
                                            }
                                        ),
                                    ),
                                }
                            ),
                        ),
                    }
                )
            ),
        }
    )
    def get(self, request):
        serializer = BoardSerializer(Board.objects.all(), many=True)
        return Response(data={'data': serializer.data}, status=status.HTTP_200_OK)


class PostDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['글'],
        operation_id='post_detail_get',
        operation_summary='글과 댓글 읽기',
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER,
                description='게시글 번호'
            ),
            openapi.Parameter(
                'ordering', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                description='댓글 정렬 규칙. 가능한 값: [시간, 최신, 좋아요]',
                default='시간',
            ),
        ],
        responses={
            200: openapi.Response(
                description='글과 댓글 읽기',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'category': openapi.Schema(type=openapi.TYPE_STRING),
                        'topic': openapi.Schema(type=openapi.TYPE_STRING),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'author': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                'image': openapi.Schema(type='null'),
                            }
                        ),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'view': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'create_at': openapi.Schema(type='DATE'),
                        'update_at': openapi.Schema(type='DATE'),
                        'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'comments': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'report': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'create_at': openapi.Schema(type='DATE'),
                                    'update_at': openapi.Schema(type='DATE'),
                                    'author': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                            'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                            'image': openapi.Schema(type='null'),
                                        }
                                    ),
                                    'parent_comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                }
                            )
                        ),
                    },
                )
            ),
            400: openapi.Response(
                description='',
            )
        }
    )
    def get(self, request, post_id):
        """
        Post and comment
        #TODO Query string 미구현
        """
        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if post.hidden:
            return Response({'msg': 'This post is hidden'}, status=status.HTTP_204_NO_CONTENT)

        post.view = post.view + 1
        post.save()

        post_serializer = PostDetailSerializer(post, user_id=request.user, many=False)

        comment_serializer = CommentSerializer(post.comment_set.filter(hidden=False), user_id=request.user, many=True)
        data = {**post_serializer.data}

        if post.board_id.category == '매거진':
            data.update({'thumbnamil': None})

        return Response({
            'data': data,
            'comments': comment_serializer.data,
        }, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        tags=['글'],
        operation_id='post_detail_post',
        operation_summary='글 수정하기',
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER,
                description='게시글 번호'
            ),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'title': openapi.Schema(type=openapi.TYPE_STRING, description='title'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='content'),
            },
        ),
        responses={
            204: openapi.Response(
                description='수정한 글',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'category': openapi.Schema(type=openapi.TYPE_STRING),
                        'topic': openapi.Schema(type=openapi.TYPE_STRING),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'author': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                'image': openapi.Schema(type='null'),
                            }
                        ),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'view': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'create_at': openapi.Schema(type='DATE'),
                        'update_at': openapi.Schema(type='DATE'),
                        'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'comments': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'report': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'create_at': openapi.Schema(type='DATE'),
                                    'update_at': openapi.Schema(type='DATE'),
                                    'author': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                            'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                            'image': openapi.Schema(type='null'),
                                        }
                                    ),
                                    'parent_comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                }
                            )
                        ),
                    },
                )
            ),
            400: openapi.Response(
                description='',
            )
        }
    )
    def post(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if request.user != post.user_id:
            return Response({'msg': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        if 'title' not in request.data:
            return Response({'msg': 'Data should have "title" field'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data['title']

        if 'content' not in request.data:
            return Response({'msg': 'Data should have "content" field'}, status=status.HTTP_400_BAD_REQUEST)

        content = request.data['content']

        if post.hidden:
            return Response({'msg': 'This post is hidden'}, status=status.HTTP_204_NO_CONTENT)

        post.title = title
        post.content = content
        post.like_post_assoc_set.filter().delete()

        serializer = PostDetailSerializer(post, user_id=request.user, many=False)
        post.save()

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['글'],
        operation_id='post_detail_delete',
        operation_summary='글 삭제하기',
        manual_parameters=[
            openapi.Parameter(
                'post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER,
                description='게시글 번호'
            ),
        ],
        responses={
            200: openapi.Response(description='삭제 성공',),
            204: openapi.Response(description='없는 댓글 삭제 시도',),
            401: openapi.Response(description='삭제 권한이 없는 댓글',)
        }
    )
    def delete(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_204_NO_CONTENT)

        if post.user_id != request.user:
            return Response({'msg': 'Unauthorized'}, status=status.HTTP_401_UNAUTHORIZED)

        try:
            liked = LikePostAssoc.objects.get(user_id=request.user, post_id=post_id)
            liked.delete()
        except Exception as e:
            pass

        post.delete()

        return Response({}, status=status.HTTP_200_OK)


class CreateOrGetPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['글'],
        operation_id='post_put',
        operation_summary='글 쓰기',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'category': openapi.Schema(type=openapi.TYPE_STRING, description='카테고리 분류 [연애, 매거진, 회사,...]'),
                'topic': openapi.Schema(type=openapi.TYPE_STRING, description='토픽 분류 [연애, 연봉, 가족,...]'),
                'mbti': openapi.Schema(type=openapi.TYPE_STRING, description='mbti 분류 [intp, entp, istj, ...]'),
                'title': openapi.Schema(type=openapi.TYPE_STRING),
                'content': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Response(
                description='글쓰기 성공. 작성한 글 반환',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'category': openapi.Schema(type=openapi.TYPE_STRING),
                        'topic': openapi.Schema(type=openapi.TYPE_STRING),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'author': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                'image': openapi.Schema(type='null'),
                            }
                        ),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'view': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'create_at': openapi.Schema(type='DATE'),
                        'update_at': openapi.Schema(type='DATE'),
                        'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        'comments': openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Items(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    'comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'content': openapi.Schema(type=openapi.TYPE_STRING),
                                    'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'report': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'create_at': openapi.Schema(type='DATE'),
                                    'update_at': openapi.Schema(type='DATE'),
                                    'author': openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                            'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                            'image': openapi.Schema(type='null'),
                                        }
                                    ),
                                    'parent_comment_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                                    'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                                }
                            )
                        ),
                    },
                )
            ),
            400: openapi.Response(description='없는 게시판 혹은 없는 토픽',),
        }
    )
    def put(self, request):
        if 'category' not in request.data:
            return Response({'msg': 'Data should have "category" field'}, status=status.HTTP_400_BAD_REQUEST)

        category = request.data['category']
        board = Board.objects.get(category=category)

        if 'topic' not in request.data:
            return Response({'msg': 'Data should have "topic" field'}, status=status.HTTP_400_BAD_REQUEST)

        text = request.data['topic']

        topic, created = Hashtag.objects.get_or_create(text=text)
        if created:
            topic.ref_count = 1
        else:
            topic.ref_count += 1
            topic.save()

        if 'mbti' not in request.data:
            return Response({'msg': 'Data should have "mbti" field'}, status=status.HTTP_400_BAD_REQUEST)

        mbti: str = request.data['mbti']
        mbti = mbti.upper()
        if not re.fullmatch(r"[IEX][SNX][TFX][PJX]", mbti):
            return Response({'msg': '\'mbti\' characters are invalid'}, status=status.HTTP_400_BAD_REQUEST)

        if 'title' not in request.data:
            return Response({'msg': 'Data should have "title" field'}, status=status.HTTP_400_BAD_REQUEST)

        title = request.data['title']

        if 'content' not in request.data:
            return Response({'msg': 'Data should have "content" field'}, status=status.HTTP_400_BAD_REQUEST)

        content = request.data['content']

        post = Post.objects.create(
            board_id=board,
            hashtag_id=topic,
            user_id=request.user,
            mbti=mbti,
            title=title,
            content=content,
            view=0,
            report=0,
            hidden=False,
        )

        post.save()
        serializer = PostDetailSerializer(post, user_id=request.user)
        return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        tags=['글', ],
        operation_id='post_list_get',
        operation_summary='글 목록',
        manual_parameters=[
            openapi.Parameter(
                'category', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                default='',
            ),
            openapi.Parameter(
                'topic', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                default='',
            ),
            openapi.Parameter(
                'mbti', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                default='',
            ),
            openapi.Parameter(
                'order', openapi.IN_QUERY, type=openapi.TYPE_STRING,
                default='', description='\'like\', \'view\' or \'create\'',
            ),
            openapi.Parameter(
                'pageSize', openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
                default=10, description='한 번에 호출하는 요약 게시글 개수. 최대 Size 100',
            ),
            openapi.Parameter(
                'pageNum', openapi.IN_QUERY, type=openapi.TYPE_NUMBER,
                default=1, description='게시글 페이지 번호. 최근에 생성된 데이터가 1 Page',
            ),
        ],
        responses={
            200: openapi.Response(
                description='글 목록',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'post_id': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'category': openapi.Schema(type=openapi.TYPE_STRING),
                        'topic': openapi.Schema(type=openapi.TYPE_STRING),
                        'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                        'author': openapi.Schema(
                            type=openapi.TYPE_OBJECT,
                            properties={
                                'nickname': openapi.Schema(type=openapi.TYPE_STRING),
                                'mbti': openapi.Schema(type=openapi.TYPE_STRING),
                                'image': openapi.Schema(type='null'),
                            }
                        ),
                        'title': openapi.Schema(type=openapi.TYPE_STRING),
                        'content': openapi.Schema(type=openapi.TYPE_STRING),
                        'view': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'like': openapi.Schema(type=openapi.TYPE_NUMBER),
                        'create_at': openapi.Schema(type='DATE'),
                        'update_at': openapi.Schema(type='DATE'),
                        'is_liked': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    },
                )
            ),
            400: openapi.Response(description='없는 게시판 혹은 없는 토픽', ),
        }
    )
    def get(self, request):
        """
        category
        topic
        mbti
        order
        pageNum
        pageSize
        """
        posts = Post.objects.filter(hidden=False)

        mbti = request.GET.get('mbti', None)
        if mbti:
            m = re.match(r'[EeIi][SsNn][TtFf][PpJj]', mbti)
            if m:
                mbti = mbti.upper()
                posts = posts.filter(mbti=mbti)

        topic = request.GET.get('topic', None)
        if topic:
            topics: list = topic.split(',')
            hashtags = Hashtag.objects.filter(text__in=topics)
            posts = posts.filter(hashtag_id__in=hashtags)

        category = request.GET.get('category', None)
        if category:
            board = Board.objects.get(category=category, hidden=False)
            posts = posts.filter(board_id=board)

        order = request.GET.get('order', None)
        if order in ['view', 'like', 'create']:
            if order == 'create': order = 'create_at'
            posts = posts.order_by(f'-{order}')

        try:
            page_size = int(request.GET.get('pageSize', '10'))
            page_num = int(request.GET.get('pageNum', '1'))
        except Exception as e:
            return Response({'msg': 'pageSize and pageNum MUST be Integer'}, status=status.HTTP_400_BAD_REQUEST)

        post_paginator = Paginator(posts, page_size)  # zero based
        paged_posts = post_paginator.get_page(page_num)
        serializer = SimplePostSerializer(paged_posts, user_id=request.user, many=True)

        return Response(data={'data': serializer.data}, status=status.HTTP_200_OK)


class LikePost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['글', ],
        operation_id='like_post_put',
        operation_summary='글 좋아요',
        manual_parameters=[
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='',),
        }
    )
    def put(self, request, post_id):
        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        liked, created = post.like_post_assoc_set.get_or_create(user_id=request.user)

        if created:
            post.like += 1
            post.save()
            serializer = SimplePostSerializer(post, user_id=request.user)

            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'The post is already liked'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['글', ],
        operation_id='like_post_delete',
        operation_summary='글 좋아요 취소',
        manual_parameters=[
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='', ),
        }
    )
    def delete(self, request, post_id):
        """
        글 좋아요 취소하기
        """
        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            liked = post.like_post_assoc_set.get(user_id=request.user)
            liked.delete()
            post.like -= 1
            post.save()
            return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_204_NO_CONTENT)


class ReportPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['신고'],
        operation_id='target_report',
        operation_summary='글, 댓글 신고하기',
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'reason': openapi.Schema(type=openapi.TYPE_STRING, description='신고 사유'),
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='신고 내용'),
            },
        ),
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='', ),
        }
    )
    def put(self, request, **kwargs):
        try:
            content = request.data['content']
            reason_text = request.data['reason']
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        try:
            reason = ReportReason.objects.get(reason=reason_text)
        except Exception as e:
            reason_list = [f"'{e.reason}'" for e in ReportReason.objects.all()]

            return Response({'msg': f'reason is available only {", ".join(reason_list)}'}, status=status.HTTP_400_BAD_REQUEST)

        target = None
        target_type = None

        # 댓글 신고 로직
        comment_id = kwargs.get('comment_id', None)
        if comment_id:
            try:
                comment = Comment.objects.get(id=comment_id)
                target = comment
                target_type = 'comment'
            except Exception as e:
                return Response({'msg': 'Not exist comment_id'}, status=status.HTTP_400_BAD_REQUEST)
        #####

        # 글 신고 로직
        post_id = kwargs.get('post_id', None)
        if post_id:
            try:
                post = Post.objects.get(id=post_id)
                target = post
                target_type = 'post'
            except Exception as e:
                return Response({'msg': 'Not exist post_id'}, status=status.HTTP_400_BAD_REQUEST)

        if target.user_id == request.user:
            return Response({'msg': 'CANNOT report yourself'}, status=status.HTTP_400_BAD_REQUEST)

        report, created = Report.objects.get_or_create(
            target_type=target_type, target_number=target.id,
            complainant_id=request.user, defendant_id=target.user_id,
            content=content, reason_id=reason
        )
        if not created:
            return Response({'msg': 'already reported'}, status=status.HTTP_202_ACCEPTED)

        return Response({}, status=status.HTTP_201_CREATED)


class LikeComment(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['댓글', ],
        operation_id='like_comment_put',
        operation_summary='댓글 좋아요',
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='', ),
        }
    )
    def put(self, request, comment_id=None):
        """
        댓글 좋아요
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Exception as e:
            return Response({'msg': str(e)}, status=status.HTTP_400_BAD_REQUEST)

        liked, created = comment.like_comment_assoc_set.get_or_create(user_id=request.user)

        if created:
            comment.like += 1
            comment.save()
            serializer = CommentSerializer(comment, user_id=request.user)
            return Response({'data': serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response({'msg': 'The post is already liked'}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['댓글', ],
        operation_id='like_comment_delete',
        operation_summary='댓글 좋아요 취소',
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='', ),
        }
    )
    def delete(self, request, comment_id=None):
        """
        댓글 좋아요 취소하기
        """
        try:
            comment = Comment.objects.get(id=comment_id)
        except Exception as e:
            return Response({'msg': 'NOT found comment_id'}, status=status.HTTP_400_BAD_REQUEST)


        try:
            liked = comment.like_comment_assoc_set.get(user_id=request.user)
            liked.delete()
            comment.like -= 1
            comment.save()

            return Response({}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'msg': 'NO liked'}, status=status.HTTP_204_NO_CONTENT)


class ReportComment(APIView):
    def put(self, request, nickname=None, comment_id=None):
        return Response({})

    def delete(self, request, nickname=None, comment_id=None):
        return Response({})


class CommentPost(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['댓글', ],
        operation_id='comment_post_put',
        operation_summary='댓글, 대댓글 쓰기',
        manual_parameters=[
            openapi.Parameter('post_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content'],
            properties={
                'content': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    description='댓글 내용. 길이는 1 이상',
                ),
                'parent_comment_id': openapi.Schema(
                    type=openapi.TYPE_NUMBER,
                    description='대댓글 작성할 경우 원댓글 id',
                ),
            },
        ),
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={

                    }
                )
            ),
            400: openapi.Response(description='',),
        }
    )
    def put(self, request, post_id):
        """
        댓글 쓰기. content의 길이는 0 이상이어야 한다.
        """
        if 'content' not in request.data:
            return Response({'msg': '\'content\' NOT in body'}, status=status.HTTP_400_BAD_REQUEST)

        if len(request.data['content']) == 0:
            return Response({'msg': '\'content\' length is 0'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            post = Post.objects.get(id=post_id)
        except Exception as e:
            return Response({'msg': 'NO post_id '}, status=status.HTTP_400_BAD_REQUEST)

        parent_comment_id = request.data.get('parent_comment_id', None)
        if 'parent_comment_id' in request.data:
            try:
                parent_comment_id = Comment.objects.get(id=parent_comment_id)
                if parent_comment_id.delete_at:
                    raise Exception('Parent comment is deleted')
            except Exception as e:
                return Response({'msg': 'NO parent_comment_id '}, status=status.HTTP_400_BAD_REQUEST)

        comment = Comment(
            user_id=request.user,
            content=request.data['content'],
            post_id=post,
            parent_comment_id=parent_comment_id,
        )

        comment.save()
        serializer = CommentSerializer(comment, user_id=request.user)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)


class CommentDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        tags=['댓글', ],
        operation_id='comment_post',
        operation_summary='댓글 수정하기',
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['content', ],
            properties={
                'content': openapi.Schema(type=openapi.TYPE_STRING, description='content. large than 0 length'),
                'parent_comment_id': openapi.Schema(type=openapi.TYPE_NUMBER, description='대댓글 작성할 때, 원 댓글의 id'),
            },
        ),
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                )
            ),
            400: openapi.Response(description='',),
        }
    )
    def post(self, request, comment_id):
        """
        댓글 수정 함수. 자신이 쓴 댓글만 수정 가능.
        """
        content = request.data.get('content', None)

        try:
            comment = Comment.objects.get(id=comment_id)

        except Exception as e:
            return Response({'msg': 'comment_id NOT found'}, status=status.HTTP_400_BAD_REQUEST)

        if comment.user_id != request.user:
            return Response({'msg': 'NO author'}, status=status.HTTP_400_BAD_REQUEST)

        if content:
            comment.content = content
            comment.save()
        else:
            return Response({'msg': 'NO empty content'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = CommentSerializer(comment, user_id=request.user)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        tags=['댓글', ],
        operation_id='comment_delete',
        operation_summary='댓글 삭제하기',
        manual_parameters=[
            openapi.Parameter('comment_id', openapi.IN_PATH, type=openapi.TYPE_NUMBER),
        ],
        responses={
            200: openapi.Response(
                description='성공',
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                    }
                ),
            ),
            400: openapi.Response(description='',),
        }
    )
    def delete(self, request, comment_id):
        """
        댓글 삭제하기
        """
        try:
            comment = Comment.objects.get(id=comment_id)
            if comment.delete_at:
                return Response({'msg': 'Already deleted comment'}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({'msg': 'comment_id NOT found'}, status=status.HTTP_400_BAD_REQUEST)

        comment.content = 'deleted'
        comment.delete_at = timezone.now()
        comment.save()

        serializer = CommentSerializer(comment, user_id=request.user)

        return Response({'data': serializer.data}, status=status.HTTP_200_OK)

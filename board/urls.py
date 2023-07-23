from django.urls import path

from board.views import *

# /boards/...
urlpatterns = [
    path('', BoardList.as_view(), name='board_list'),

    path('posts/<int:post_id>/like/', LikePost.as_view(), name='like_post'),
    path('posts/<int:post_id>/comment/', CommentPost.as_view(), name='comment_post'),
    path('posts/<int:post_id>/report/', ReportPost.as_view(), name='post_report'),
    path('posts/<int:post_id>/', PostDetail.as_view(), name='post_detail'),
    path('posts/', CreateOrGetPost.as_view(), name='create_post_detail'),

    path('comments/<int:comment_id>/like/', LikeComment.as_view(), name='like_post'),
    path('comments/<int:comment_id>/report/', ReportPost.as_view(), name='comment_report'),
    path('comments/<int:comment_id>/', CommentDetail.as_view(), name='comment_detail'),
]

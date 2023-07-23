from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.validators import RegexValidator
from django.db import models
from uuid import uuid4

from hashtag.models import Hashtag
from mbti.models import MBTIClass

GENDER_CHOICES = (
    (0, 'Male'), (1, 'Female'), (2, 'Unknown')
)


class UserManager(BaseUserManager):
    def create_user(self, nickname, password=None, gender=2, phone=None, email=None, image=None):
        user = self.model(nickname=nickname, gender=gender, phone=phone, email=self.normalize_email(email), image=image)
        # user.set_password(password)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, nickname, password, gender=2, phone=None, email=None, image=None):
        user = self.model(nickname=nickname, gender=gender, phone=phone, email=self.normalize_email(email), image=image)
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    nickname = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=50, null=True, blank=True)
    gender = models.SmallIntegerField(choices=GENDER_CHOICES, default=2)
    phone = models.CharField(max_length=12, blank=True, unique=True, null=True)
    email = models.EmailField(blank=True, null=True)
    image = models.ImageField(upload_to="user_image/", blank=True, null=True)
    is_init = models.BooleanField(default=False, null=False, blank=False)
    # set_mbti = models.BooleanField(default=False, null=False, blank=False)
    mbti = models.CharField(max_length=4, default='xxxx', validators=[RegexValidator(regex=r"[IEx][SNx][TFx][PJx]", message='Not match MBTI Characters')])

    create_at = models.DateTimeField(auto_now_add=True, editable=False)
    update_at = models.DateTimeField(auto_now=True)

    is_superuser = models.BooleanField(default=False, null=False, blank=False)
    is_staff = models.BooleanField(default=False, null=False, blank=False)

    class Meta:
        db_table = 'user'

    objects = UserManager()

    USERNAME_FIELD = 'nickname'
    EMAIL_FIELD = 'email'
    REQUIRED_FIELDS = []


class OpenAuth(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.SET_NULL, db_column='user_id', null=True, blank=True, related_name='open_auth')
    kakao = models.CharField(max_length=100, unique=True, null=True, blank=True)
    naver = models.CharField(max_length=100, unique=True, null=True, blank=True)
    google = models.CharField(max_length=100, unique=True, null=True, blank=True)
    apple = models.CharField(max_length=100, unique=True, null=True, blank=True)

    kakao_update_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    naver_update_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    google_update_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    apple_update_at = models.DateTimeField(auto_now=False, null=True, blank=True)

    kakao_delete_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    naver_delete_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    google_delete_at = models.DateTimeField(auto_now=False, null=True, blank=True)
    apple_delete_at = models.DateTimeField(auto_now=False, null=True, blank=True)

    class Meta:
        db_table = 'user_oauth'
        verbose_name = 'Social authentication'

    def __str__(self):
        return f"{self.user_id} {self.kakao}"


class UserInterest(models.Model):
    user_id = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user_id', null=True, blank=True, related_name='user_interest')
    mbtis = models.ManyToManyField(MBTIClass, )
    interests = models.ManyToManyField(Hashtag, )

    class Meta:
        db_table = 'user interest'
        verbose_name = '유저 관심 정보'

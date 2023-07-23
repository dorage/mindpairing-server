from django.db import models
from membership.models import User


class Terms(models.Model):
    index = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255, null=False, blank=False)
    content = models.TextField()
    mandatory = models.BooleanField(null=False, blank=False)
    create_at = models.DateTimeField(auto_now_add=True, editable=False)

    class Meta:
        db_table = 'terms'
        verbose_name = 'Terms'

    def __str__(self):
        return f"({self.index}) {self.title}({self.mandatory})"


class Agreement(models.Model):
    user_id = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='agreement_set')
    terms_id = models.ForeignKey(Terms, on_delete=models.CASCADE, db_column='term_id', related_name='agreement_set')
    agreement = models.BooleanField(default=False, null=False, blank=False)
    create_at = models.DateTimeField(auto_now_add=True, editable=False)
    update_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'terms_agreement'
        verbose_name = 'Terms Agreement'

    def __str__(self):
        return f"{self.terms_id.title} {self.user_id} {self.agreement} {self.update_at}"

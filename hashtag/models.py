from django.db import models


class Hashtag(models.Model):
    text = models.CharField(max_length=20, null=False, blank=False, unique=True, editable=True)
    ref_count = models.PositiveIntegerField(default=1)

    class Meta:
        db_table = 'hashtag'

    def __str__(self):
        return f"#{self.text}"

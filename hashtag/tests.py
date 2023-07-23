from django.test import TestCase

# Create your tests here.
from .models import *
from itertools import product


prod = product(*[['E', 'I'], ['S', 'N'], ['T', 'F'], ['P', 'J']])

for p in prod:
    Hashtag.objects.create(content=''.join(p), ref_count=0).save()

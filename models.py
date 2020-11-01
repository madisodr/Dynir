from django.db import models
from jsonfield import JSONField

class Images(models.Model):
    unique_id = models.CharField(max_length=32, primary_key=True, unique=True)
    image = models.ImageField(upload_to='images/', null=True)
    colors = JSONField() # json field of two color hex codes {"colors": [#ffff00, #ff00ff]}
    # upload_date = models.DateTimeField('date published')

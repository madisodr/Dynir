from django.db import models
from jsonfield import JSONField

"""Images db model
unique_id: An md5 hash of the image
image: the location in storage of the image
colors: json field of two color hex codes {"c0": "#1c0431", "c1": "#6d44b4"}
"""
class Images(models.Model):
    unique_id = models.CharField(max_length=32, primary_key=True, unique=True)
    image = models.ImageField(upload_to='images/', null=True)
    colors = JSONField()

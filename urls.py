from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from .views import *

urlpatterns = [
    #re_path(r'^(?P<file_name>\w+).(?P<extension>(\w+)?)$', views.handle_image_request, name='handle_image_request'),
    # re_path(r'^(?P<file_name>dumblr_[\w+)_(?P<width>\d+).(?P<extension>(\w+)?)$', views.handle_image_request, name='handle_image_request'),
    re_path(r'^(?P<file_name>dumblr_.{17})_(?P<width>\d+)(?P<square>sq)?.(?P<output_content_type>png|jpg|gif|webp)$', views.handle_image_request, name='handle_image_request'),
    path('', views.index, name='index'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

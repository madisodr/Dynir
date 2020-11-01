from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from django.shortcuts import render, redirect
from django.conf import settings
from . import views, imagemagick
from .models import Images

import hashlib
import os
import logging
import hashlib
import json

logger = logging.getLogger(__name__)

def index(request):
    return HttpResponse("Welcome to the ImageResizer. This is an app written in Django that uses opencv and imagemagick in order to perform a set of operations on images such as resizing, format conversion, compression, and content-aware cropping.")

def handle_image_request(request, file_name: str, output_content_type: str, width: int=None):
    resizing_flag = False
    format_conversion = False

    if not imagemagick.is_valid_filetype(output_content_type):
        raise Http404

    if width is not None:
        width = int(width)
        resizing_flag = True

        if width > settings.RESIZER_MAX_WIDTH:
            raise Http404

    source_file = ""
    source_content_type = ""

    # Try to find the source file
    for content_type in settings.MIMETYPES:
        source_file = "%s/%s.%s" % (settings.MEDIA_ROOT, file_name, content_type)
        if file_exists(source_file):
            source_content_type = content_type
            break

    # Read the source file as binary data for manipulation
    processed_image_data = _open(source_file)

    image_md5_hash = generate_md5(processed_image_data)

    # Image Manipulation Block
    if resizing_flag:
        try:
            processed_image_data = imagemagick.resize(processed_image_data, width)
        except Exception as e:
            raise Http404(e)

    if source_content_type != output_content_type:
        try:
            processed_image_data = imagemagick.convert(processed_image_data, output_content_type)
        except Exception as e:
            raise Http404(e)

    colors = imagemagick.extract_primary_colors(processed_image_data)
    json_colors = json.dumps(colors)

    image_db_data = Images(unique_id=image_md5_hash, image=source_file, colors=json_colors)
    image_db_data.save()

    if processed_image_data is None:
        raise Http404

    return render_binary_image_response(processed_image_data, output_content_type)

def _open(file_name: str) -> bytes:
    return open(file_name, 'rb')

def render_binary_image_response(image_data: bytes, image_content_type: str) -> HttpResponse:
    return HttpResponse(image_data, content_type=settings.MIMETYPES[image_content_type])

def file_exists(file_name: str) -> bytes:
    if os.path.isfile(file_name):
        return True
    else:
        return False

def generate_md5(image_data: bytes):
    md5_hash = hashlib.md5()
    md5_hash.update(repr(image_data).encode('utf-8'))
    return md5_hash.hexdigest()

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

"""Handles the index location"""
def index(request):
    all_images = Images.objects.all()
    sizes = ['75sq', '250', '500']

    return render(request, 'index.html', {'images': all_images, 'sizes': sizes})

"""Handles a specific image request
file_name(str) : name of the file being requested
output_content_type(str): the expected content type to get back
width(int): the width of the image we want to fetch
square(str): whether or not the image should be cropped as a square
"""
def handle_image_request(request, file_name: str, output_content_type: str, width: int=None, square: str=""):
    resizing_flag = False
    format_conversion = False
    square_crop = False

    """ Validate parameters first """
    if not imagemagick.is_valid_filetype(output_content_type):
        raise Http404

    if width is not None:
        width = int(width)
        resizing_flag = True

        if width > settings.RESIZER_MAX_WIDTH:
            raise Http404

    if square != "":
        square_crop = True

    source_file = ""
    source_content_type = ""

    """ Try to find the source file
        TODO Just save the filetype in the database on upload so we don't have to look it up like this, just go straight
        to the image. Duh!
    """
    for content_type in settings.MIMETYPES:
        source_file = "%s/%s.%s" % (settings.MEDIA_ROOT, file_name, content_type)
        if file_exists(source_file):
            source_content_type = content_type
            break

    """ Read the source file as binary data for manipulation """
    processed_image_data = _open(source_file)

    """ Image Manipulation Block """
    if resizing_flag:
        try:
            processed_image_data = imagemagick.resize_and_crop(processed_image_data, width, square_crop)
        except Exception as e:
            raise Http404(e)

    if source_content_type != output_content_type:
        try:
            processed_image_data = imagemagick.convert(processed_image_data, output_content_type)
        except Exception as e:
            raise Http404(e)

    if processed_image_data is None:
        raise Http404

    return render_binary_image_response(processed_image_data, output_content_type)

""" Handles the uploading of an image """
def handle_upload_image_request(request):
    image_md5_hash = generate_md5(processed_image_data)
    colors = imagemagick.extract_primary_colors(processed_image_data)
    json_colors = json.dumps(colors)

    image_db_data = Images(unique_id=image_md5_hash, image=file_name, colors=json_colors)
    image_db_data.save()

"""Opens a file to be read in as bytes
file_name(str): the file to be opened
returns bytes
"""
def _open(file_name: str) -> bytes:
    return open(file_name, 'rb')

""" Renders the HttpReponse for an image
image_data(bytes): The data containing the processed image
image_content_type(str): see settings.MIMETYPES for allowed content types
"""
def render_binary_image_response(image_data: bytes, image_content_type: str) -> HttpResponse:
    return HttpResponse(image_data, content_type=settings.MIMETYPES[image_content_type])

""" Checks the existence of a file
file_name(str): file to look for
"""
def file_exists(file_name: str) -> bytes:
    if os.path.isfile(file_name):
        return True
    else:
        return False

""" Generates an md5 hash based on an image
image_data(bytes): the image in a byte format
"""
def generate_md5(image_data: bytes):
    md5_hash = hashlib.md5()
    md5_hash.update(repr(image_data).encode('utf-8'))
    return md5_hash.hexdigest()

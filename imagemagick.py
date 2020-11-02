from __future__ import with_statement

from django.conf import settings
from wand.image import Image
from wand.color import Color

"""Method to resize and crop an image based on supplied parameters
source_image_data(bytes): the image to convert
scaled_width(int): width to scale the image too, maintaining proper aspect ratios
square_crop(bool): whether or not to to a square cropping of the image. Useful for avatars
returns image data as bytes
"""
def resize_and_crop(source_image_data: bytes, scaled_width: int, square_crop: bool) -> bytes:
    cloned_bin = None

    with Image(blob=source_image_data) as original:
        aspect_ratio = float(original.width / original.height)
        scaled_height = int(scaled_width / aspect_ratio)

        with original.clone() as cloned:
            cloned.resize(scaled_width, scaled_height)

            if square_crop is True:
                cloned.liquid_rescale(scaled_width, scaled_width)

            cloned_bin = cloned.make_blob(cloned.format)

    return cloned_bin

""" Converts an image from one file type to another
    TODO Handle gif and webp. Currently only works with png and jpg
source_image_data(bytes): the image to convert
new_content_type(str): the content type to convert too
returns image data as bytes
"""
def convert(source_image_data: bytes, new_content_type: str) -> bytes:
    if not is_valid_filetype(new_content_type):
        raise Exception("Invalid Filetype")

    converted_bin = None

    with Image(blob=source_image_data) as original:
        with original.clone() as cloned:
            converted_bin = cloned.make_blob(new_content_type)

    return converted_bin

""" Clamp an rgb int between [0, 255]
"""
def hex_clamp(rgb: int) -> int:
      return max(0, min(rgb, 255))

""" Determine the two dominant colors within an image
source_image_data(bytes): the image
returns a dictionary holding hex colors.
"""
def extract_primary_colors(source_image_data: bytes):
    colors = {"c0": "", "c1" : ""}

    with Image(blob=source_image_data) as original:
        with original.clone() as cloned:
            cloned.quantize(2, 'rgb', 0, False, False)
            hist = cloned.histogram
            for i, c in enumerate(hist):
                key = "c" + str(i)
                colors[key] = "#{0:02x}{1:02x}{2:02x}".format(hex_clamp(c.red_int8),hex_clamp(c.green_int8),hex_clamp(c.blue_int8))

    return colors

""" Validate supplied content type with the allowed MIMETYPES
content_type(str): The content type to validate
returns bool
"""
def is_valid_filetype(content_type: str) -> bool:
    if (content_type in settings.MIMETYPES):
        return True
    else:
        return False

from __future__ import with_statement

from django.conf import settings
from wand.image import Image
from wand.color import Color

def resize(source_image_data: bytes, scaled_width: int) -> bytes:
    cloned_bin = None

    with Image(blob=source_image_data) as original:
        aspect_ratio = float(original.width / original.height)
        scaled_height = int(scaled_width / aspect_ratio)

        with original.clone() as cloned:
            cloned.resize(scaled_width, scaled_height)
            cloned_bin = cloned.make_blob(cloned.format)

    return cloned_bin

def convert(source_image_data: bytes, new_content_type: str) -> bytes:
    if not is_valid_filetype(new_content_type):
        raise Exception("Invalid Filetype")

    converted_bin = None

    with Image(blob=source_image_data) as original:
        with original.clone() as cloned:
            converted_bin = cloned.make_blob(new_content_type)

    return converted_bin

def hex_clamp(rgb: int) -> int:
      return max(0, min(rgb, 255))

def extract_primary_colors(source_image_data: bytes):
    colors = []

    with Image(blob=source_image_data) as original:
        with original.clone() as cloned:
            cloned.quantize(2, 'rgb', 0, False, False)
            hist = cloned.histogram
            for c in hist:
                colors.append("#{0:02x}{1:02x}{2:02x}".format(hex_clamp(c.red_int8),hex_clamp(c.green_int8),hex_clamp(c.blue_int8)))

    return colors

def is_valid_filetype(content_type: str) -> bool:
    if (content_type in settings.MIMETYPES):
        return True
    else:
        return False

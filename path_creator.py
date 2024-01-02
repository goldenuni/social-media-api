import os
import uuid

from django.utils.text import slugify


def image_file_path(instance, filename):
    _, extension = os.path.splitext(filename)
    directory = slugify(instance)
    filename = f"{slugify(instance)}-{uuid.uuid4()}{extension}"

    return os.path.join("uploads", "social_media", directory, filename)

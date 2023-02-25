import base64

from django.core.files.base import ContentFile


def base64_to_file(data, name=None):
    _format, _img_str = data.split(";base64,")
    _name, ext = _format.split("/")
    if not name:
        name = _name.split(":")[-1]
    return ContentFile(base64.b64decode(_img_str), name=f"{name}.{ext}")


def file_to_base64(file):
    with open(file.path, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read()).decode("utf-8")
    encoded_string = f"data:image/{file.name.split('.')[-1]};base64,{encoded_string}"
    return encoded_string

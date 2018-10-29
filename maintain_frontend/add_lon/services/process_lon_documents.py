import uuid
from werkzeug.utils import escape


def escape_filename(string):
    return escape(string)


def generate_uuid():
    return str(uuid.uuid4())


def bucket():
    return 'lon'

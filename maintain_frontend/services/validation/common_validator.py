import re
from datetime import datetime
from shapely.geometry import shape


class CommonValidator(object):
    @staticmethod
    def is_required(value):
        """Checks if the data provided is not empty."""
        return True if value else False

    @staticmethod
    def is_email(value):
        """Checks if the data provided is a valid email format."""
        return True if re.match(r"[^@]+@[^@]+\.[^@]+", value) else False

    @staticmethod
    def is_length_less_than_or_equal_to(value, length):
        """Checks if the data provided is less than or equal to the specified length."""
        return True if len(value) <= length else False

    @staticmethod
    def is_length_equal_to(value, length):
        """Checks if the data provided is equal to the specified length."""
        return True if len(value) == length else False

    @staticmethod
    def is_number_with_zero_or_x_decimal_places(value, decimal_places):
        if re.match(r"^\d+(?:\.\d{%s})?$" % decimal_places, value):
            if float(value) > 0:
                return True
        return False

    @staticmethod
    def is_number_with_zero_or_up_to_x_decimal_places(value, decimal_places):
        if re.match(r"^\d+(?:\.\d{1,%s})?$" % decimal_places, value):
            if float(value) > 0:
                return True
        return False

    @staticmethod
    def is_number_x_length_y_decimal_places(value, length, decimal_places):
        if re.match(r"^\d{1,%s}\.\d{%s}$" % (length, decimal_places), value):
            if float(value) > 0:
                return True
        return False

    @staticmethod
    def is_positive_number(value):
        return float(value) > 0

    @staticmethod
    def is_positive_number_or_zero(value):
        return float(value) >= 0

    @staticmethod
    def is_int(value):
        try:
            value = int(value)
        except Exception as e:
            pass
        return isinstance(value, int)

    @staticmethod
    def is_number_x_length_up_to_y_decimal_places(value, length, decimal_places):
        if re.match(r"^\d{1,%s}(?:\.\d{1,%s})?$" % (length, decimal_places), value):
            if float(value) > 0:
                return True
        return False

    @staticmethod
    def is_valid_date(date_parts):
        """Checks if an array of day, month and year strings provided represents a valid date."""
        if not date_parts or len(date_parts) != 3 or not isinstance(date_parts, list):
            return False

        try:
            day = date_parts[0]
            month = date_parts[1]
            year = date_parts[2]

            CommonValidator.build_date(day, month, year)
            return True
        except (ValueError, OverflowError):
            return False

    @staticmethod
    def is_phone_number(value):
        """Checks if the data provided is a valid phone number. All numeric, allow only single space between number."""
        return True if re.match(r"^[\d]+( [\d]+)*$", value) else False

    @staticmethod
    def is_postcode(value):
        """Checks if the data provided is a valid postcode."""
        postcode_regex_check = '^([Gg][Ii][Rr] 0[Aa]{2})|((([A-Za-z][0-9]{1,2})|(([A-Za-z]' \
                               '[A-Ha-hJ-Yj-y][0-9]{1,2})|(([A-Za-z][0-9][A-Za-z])|' \
                               '([A-Za-z][A-Ha-hJ-Yj-y][0-9]?[A-Za-z])))) [0-9][A-Za-z]{2})$'

        return True if re.match(postcode_regex_check, value) else False

    @staticmethod
    def is_past_date(day, month, year):
        """Checks if an array of day, month and year represents a date in the past or the current date."""
        try:
            date = CommonValidator.build_date(day, month, year)
            return date < datetime.now()
        except (ValueError, OverflowError):
            return False

    @staticmethod
    def is_past_or_present_date(day, month, year):
        """Checks if an array of day, month and year represents a date in the past or the current date."""
        try:
            date = CommonValidator.build_date(day, month, year)
            return date <= datetime.now()
        except (ValueError, OverflowError):
            return False

    @staticmethod
    def is_future_date(day, month, year):
        """Checks if an array of day, month and year represents a date in the future."""
        try:
            date = CommonValidator.build_date(day, month, year)
            return date > datetime.now()
        except (ValueError, OverflowError):
            return False

    @staticmethod
    def is_later_than_date(first_date, second_date):
        """Checks if a date after another."""
        return first_date > second_date

    @staticmethod
    def build_date(day, month, year):
        return datetime(int(year), int(month), int(day))

    @staticmethod
    def is_pdf(mime_type):
        return '/' in mime_type and mime_type.rsplit('/', 1)[1].lower() in 'pdf'

    @staticmethod
    def does_string_contain(value, character):
        if re.search(r"[%s]" % character, value):
            return True
        return False

    @staticmethod
    def check_geometry(feature, checks):
        if 'geometry' not in feature:
            return False
        geo_shape = shape(feature['geometry'])
        if 'is_simple' in checks:
            if not geo_shape.is_simple:
                return False
        if 'is_valid' in checks:
            if not geo_shape.is_valid:
                return False
        if 'zero_length' in checks:
            if feature['geometry']['type'] == 'LineString' and geo_shape.length == 0.0:
                return False
        if 'zero_area' in checks:
            if feature['geometry']['type'] == 'Polygon' and geo_shape.area == 0.0:
                return False
        return True

    @staticmethod
    def is_uploaded_filesize_less_than_bytes(file, no_of_bytes):
        if file:
            file.seek(0, 2)
            file_length = file.tell()
            file.seek(0)

            return file_length <= no_of_bytes
        else:
            return False

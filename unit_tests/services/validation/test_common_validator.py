from unittest import TestCase
from datetime import datetime

from maintain_frontend.services.validation.common_validator import CommonValidator

EMPTY_STRING = ''
VALID_DATA = 'some data'
VALID_EMAIL = 'test@test.com'
INVALID_EMAIL = 'invalid email'
VALID_PHONE = '01234 567890'
INVALID_PHONE = 'test'
NINE_CHARS = '9 chars..'
TEN_CHARS = '10 chars..'
ELEVEN_CHARS = '11 chars...'

VALID_DAY = '15'
VALID_MONTH = '5'
VALID_PAST_DATE = '2000'
VALID_FUTURE_DATE = '3000'

CURRENT_DAY = datetime.now().day
CURRENT_MONTH = datetime.now().month
CURRENT_YEAR = datetime.now().year

INVALID_DAY = '32'
INVALID_MONTH = '13'
INVALID_YEAR = '0'

POSITIVE_NUMBER = 12345
NEGATIVE_NUMBER = -12345
ZERO = 0

VALID_DATE = ['12', '12', '2020']
VALID_DATE_MIN = ['1', '1', '1']
VALID_DATE_MAX = ['12', '12', '9999']
VALID_DATE_LEADING_ZEROES = ['0012', '0012', '02020']
INVALID_DATE_LETTERS = ['AA', 'AA', 'AAAA']
INVALID_DATE_DAY = ['60', '12', '2020']
INVALID_DATE_MONTH = ['12', '60', '2020']
INVALID_DATE_YEAR = ['12', '12', '99999']
INVALID_DATE_DAY_NOT_IN_MONTH = ['30', '02', '2020']
INVALID_DATE_LENGTHS = ['123', '123', '2020']
INVALID_DATE_NONE = None
INVALID_DATE_EMPTY_LIST = []
INVALID_DATE_EMPTY_STRING = ''
INVALID_DATE_NONEMPTY_STRING = '12122020'
INVALID_DATE_ZERO_BASED = ['0', '0', '2020']
INVALID_DATE_TRAILING_ZEROES = ['1200', '1200', '002020']
INVALID_DATE_LIST_OF_EMPTY_STRINGS = ['', '', '']

MIME_TYPE = {
    "pdf": "application/pdf",
    "text": "text/plain"
}

BAD_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            534030,
                            180510
                        ],
                        [
                            534622.5,
                            180522.5
                        ],
                        [
                            534035,
                            179905
                        ],
                        [
                            534652.5,
                            179890
                        ],
                        [
                            534030,
                            180510
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        534305,
                        180680
                    ],
                    [
                        534305,
                        180680
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            534305,
                            180680
                        ],
                        [
                            534305,
                            180680
                        ],
                        [
                            534305,
                            180680
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        534062.5,
                        180582.5
                    ],
                    [
                        534917.5,
                        180587.5
                    ],
                    [
                        534100,
                        179710
                    ],
                    [
                        534617.5,
                        180960
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {}
        }
    ]
}

GOOD_GEOJSON = {
    "type": "FeatureCollection",
    "features": [
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "Polygon",
                "coordinates": [
                    [
                        [
                            534117.73,
                            180731.51
                        ],
                        [
                            534115,
                            180835
                        ],
                        [
                            534247.27,
                            180838.49
                        ],
                        [
                            534250,
                            180735
                        ],
                        [
                            534117.73,
                            180731.51
                        ]
                    ]
                ]
            }
        },
        {
            "type": "Feature",
            "properties": {},
            "geometry": {
                "type": "LineString",
                "coordinates": [
                    [
                        533517.5,
                        180702.5
                    ],
                    [
                        533482.5,
                        179910
                    ]
                ]
            }
        }
    ]
}


class TestCommonValidator(TestCase):
    def test_is_required_false_when_input_empty(self):
        result = CommonValidator.is_required(EMPTY_STRING)

        self.assertFalse(result)

    def test_is_required_true_when_input_provided(self):
        result = CommonValidator.is_required(VALID_DATA)

        self.assertTrue(result)

    def test_is_email_false_when_email_invalid(self):
        result = CommonValidator.is_email(INVALID_EMAIL)

        self.assertFalse(result)

    def test_is_email_true_when_email_valid(self):
        result = CommonValidator.is_email(VALID_EMAIL)

        self.assertTrue(result)

    def test_is_less_than_length_true_for_short_value(self):
        result = CommonValidator.is_length_less_than_or_equal_to(NINE_CHARS, 10)

        self.assertTrue(result)

    def test_is_less_than_length_false_for_long_value(self):
        result = CommonValidator.is_length_less_than_or_equal_to(ELEVEN_CHARS, 10)

        self.assertFalse(result)

    def test_is_less_than_length_true_for_same_value(self):
        result = CommonValidator.is_length_less_than_or_equal_to(TEN_CHARS, 10)

        self.assertTrue(result)

    def test_is_phone_number_false_when_phone_invalid(self):
        result = CommonValidator.is_phone_number(INVALID_PHONE)

        self.assertFalse(result)

    def test_is_phone_number_true_when_phone_valid(self):
        result = CommonValidator.is_phone_number(VALID_PHONE)

        self.assertTrue(result)

    def test_is_valid_date_true_for_valid_date(self):
        result = CommonValidator.is_valid_date(VALID_DATE)

        self.assertTrue(result)

    def test_is_valid_date_true_for_valid_date_min(self):
        result = CommonValidator.is_valid_date(VALID_DATE_MIN)

        self.assertTrue(result)

    def test_is_valid_date_true_for_valid_date_max(self):
        result = CommonValidator.is_valid_date(VALID_DATE_MAX)

        self.assertTrue(result)

    def test_is_valid_date_false_for_leading_zeroes(self):
        result = CommonValidator.is_valid_date(VALID_DATE_LEADING_ZEROES)

        self.assertTrue(result)

    def test_is_valid_date_false_for_date_with_letters(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_LETTERS)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_with_day_out_of_range(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_DAY)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_with_month_out_of_range(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_MONTH)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_with_year_out_of_range(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_YEAR)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_with_day_not_in_month(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_DAY_NOT_IN_MONTH)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_with_invalid_lengths(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_LENGTHS)

        self.assertFalse(result)

    def test_is_valid_date_false_for_date_as_none(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_NONE)

        self.assertFalse(result)

    def test_is_valid_date_false_for_empty_list(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_EMPTY_LIST)

        self.assertFalse(result)

    def test_is_valid_date_false_for_empty_string(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_EMPTY_STRING)

        self.assertFalse(result)

    def test_is_valid_date_false_for_nonempty_string(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_NONEMPTY_STRING)

        self.assertFalse(result)

    def test_is_valid_date_false_for_zero_based_inputs(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_ZERO_BASED)

        self.assertFalse(result)

    def test_is_valid_date_false_for_trailing_zeroes(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_TRAILING_ZEROES)

        self.assertFalse(result)

    def test_is_valid_date_false_for_list_of_empty_strings(self):
        result = CommonValidator.is_valid_date(INVALID_DATE_LIST_OF_EMPTY_STRINGS)

        self.assertFalse(result)

    def test_is_past_date_with_past_date(self):
        result = CommonValidator.is_past_date(VALID_DAY, VALID_MONTH, VALID_PAST_DATE)

        self.assertTrue(result)

    def test_is_past_date_with_future_date(self):
        result = CommonValidator.is_past_date(VALID_DAY, VALID_MONTH, VALID_FUTURE_DATE)

        self.assertFalse(result)

    def test_is_past_date_with_current_date(self):
        result = CommonValidator.is_past_date(CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR)

        self.assertTrue(result)

    def test_is_past_date_with_invalid_date(self):
        result = CommonValidator.is_past_date(INVALID_DAY, INVALID_MONTH, INVALID_YEAR)

        self.assertFalse(result)

    def test_is_future_date_with_future_date(self):
        result = CommonValidator.is_future_date(VALID_DAY, VALID_MONTH, VALID_FUTURE_DATE)

        self.assertTrue(result)

    def test_is_future_date_with_past_date(self):
        result = CommonValidator.is_future_date(VALID_DAY, VALID_MONTH, VALID_PAST_DATE)

        self.assertFalse(result)

    def test_is_future_date_with_current_date(self):
        result = CommonValidator.is_future_date(CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR)

        self.assertFalse(result)

    def test_is_future_date_with_invalid_date(self):
        result = CommonValidator.is_future_date(INVALID_DAY, INVALID_MONTH, INVALID_YEAR)

        self.assertFalse(result)

    def test_is_pdf_with_pdf(self):
        result = CommonValidator.is_pdf(MIME_TYPE['pdf'])

        self.assertTrue(result)

    def test_is_pdf_with_text(self):
        result = CommonValidator.is_pdf(MIME_TYPE['text'])

        self.assertFalse(result)

    def test_bad_geojson_simple(self):
        result = CommonValidator.check_geometry(BAD_GEOJSON['features'][3], 'is_simple')

        self.assertFalse(result)

    def test_good_geojson_simple(self):
        result = CommonValidator.check_geometry(GOOD_GEOJSON['features'][1], 'is_simple')

        self.assertTrue(result)

    def test_bad_geojson_valid(self):
        result = CommonValidator.check_geometry(BAD_GEOJSON['features'][0], 'is_valid')

        self.assertFalse(result)

    def test_good_geojson_valid(self):
        result = CommonValidator.check_geometry(GOOD_GEOJSON['features'][0], 'is_valid')

        self.assertTrue(result)

    def test_bad_geojson_zero_length(self):
        result = CommonValidator.check_geometry(BAD_GEOJSON['features'][1], 'zero_length')

        self.assertFalse(result)

    def test_good_geojson_zero_length(self):
        result = CommonValidator.check_geometry(GOOD_GEOJSON['features'][1], 'zero_length')

        self.assertTrue(result)

    def test_bad_geojson_zero_area(self):
        result = CommonValidator.check_geometry(BAD_GEOJSON['features'][2], 'zero_area')

        self.assertFalse(result)

    def test_good_geojson_zero_area(self):
        result = CommonValidator.check_geometry(GOOD_GEOJSON['features'][0], 'zero_area')

        self.assertTrue(result)

    def test_bad_geojson_no_geo(self):
        result = CommonValidator.check_geometry(BAD_GEOJSON['features'][4], 'zero_area')

        self.assertFalse(result)

    def test_is_length_equal_to_true(self):
        result = CommonValidator.is_length_equal_to(NINE_CHARS, 9)

        self.assertTrue(result)

    def test_is_length_equal_to_false(self):
        result = CommonValidator.is_length_equal_to(NINE_CHARS, 10)

        self.assertFalse(result)

    def test_is_positive_number_true(self):
        result = CommonValidator.is_positive_number(POSITIVE_NUMBER)

        self.assertTrue(result)

    def test_is_positive_number_false(self):
        result = CommonValidator.is_positive_number(NEGATIVE_NUMBER)

        self.assertFalse(result)

    def test_is_positive_number_or_zero_true(self):
        result = CommonValidator.is_positive_number_or_zero(POSITIVE_NUMBER)

        self.assertTrue(result)

    def test_is_positive_number_or_zero_true_for_zero(self):
        result = CommonValidator.is_positive_number_or_zero(ZERO)

        self.assertTrue(result)

    def test_is_positive_number_or_zero_false(self):
        result = CommonValidator.is_positive_number_or_zero(NEGATIVE_NUMBER)

        self.assertFalse(result)

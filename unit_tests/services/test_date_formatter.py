import datetime
import calendar
from maintain_frontend.services.date_formatter import DateFormatter
from unittest import TestCase

VALID_DAY = '15'
VALID_MONTH = '11'
VALID_YEAR = '2000'

INVALID_DAY = '32'
INVALID_MONTH = '13'
INVALID_YEAR = '0'

DAYLIGHT_SAVINGS_MONTH = 7
NON_DAYLIGHT_SAVINGS_MONTH = 1

DATE_FORMAT = '%-d %B %Y'
TIME_FORMAT = '%H:%M:%S'


class TestDateFormatter(TestCase):

    def test_to_iso_format_undefined_inputs(self):
        date = DateFormatter.to_iso_format(None, None, None)
        self.assertFalse(date)

    def test_to_iso_format_invalid_inputs(self):
        self.assertRaises(
            ValueError,
            DateFormatter.to_iso_format, INVALID_DAY, INVALID_MONTH, INVALID_YEAR
        )

    def test_to_iso_format_valid_inputs(self):
        expected_date = '{}-{}-{}'.format(VALID_YEAR, VALID_MONTH, VALID_DAY)
        actual_date = DateFormatter.to_iso_format(VALID_DAY, VALID_MONTH, VALID_YEAR)
        self.assertEqual(actual_date, expected_date)

    def test_to_display_format_undefined_inputs(self):
        date = DateFormatter.to_display_format(None, None, None)
        self.assertFalse(date)

    def test_to_display_format_invalid_inputs(self):
        self.assertRaises(
            ValueError,
            DateFormatter.to_display_format, INVALID_DAY, INVALID_MONTH, INVALID_YEAR
        )

    def test_to_display_format_valid_inputs(self):
        expected_date = '{}-{}-{}'.format(VALID_DAY, VALID_MONTH, VALID_YEAR)
        actual_date = DateFormatter.to_display_format(VALID_DAY, VALID_MONTH, VALID_YEAR)
        self.assertEqual(actual_date, expected_date)

    def test_format_date_bst_non_daylight_savings(self):
        object_datetime = datetime.datetime(int(VALID_YEAR), NON_DAYLIGHT_SAVINGS_MONTH, int(VALID_DAY)).replace(
            hour=10,
            minute=0,
            second=0
        )

        expected_time = '{}:{}:{}'.format(
            format(object_datetime.hour, '02'),
            format(object_datetime.minute, '02'),
            format(object_datetime.second, '02')
        )
        actual_time = DateFormatter.format_date_bst(object_datetime, TIME_FORMAT)

        self.assertEqual(actual_time, expected_time)

    def test_format_date_bst_daylight_savings(self):
        object_datetime = datetime.datetime(int(VALID_YEAR), DAYLIGHT_SAVINGS_MONTH, int(VALID_DAY)).replace(
            hour=10,
            minute=0,
            second=0
        )

        expected_time = '{}:{}:{}'.format(
            format(object_datetime.hour + 1, '02'),
            format(object_datetime.minute, '02'),
            format(object_datetime.second, '02')
        )

        actual_time = DateFormatter.format_date_bst(object_datetime, TIME_FORMAT)

        self.assertEqual(actual_time, expected_time)

    def test_format_date_bst_daylight_savings_date_correct(self):
        object_datetime = datetime.datetime(int(VALID_YEAR), DAYLIGHT_SAVINGS_MONTH, int(VALID_DAY)).replace(
            hour=23,
            minute=30,
            second=0
        )

        expected_date = '{} {} {}'.format(
            object_datetime.day + 1,
            calendar.month_name[object_datetime.month],
            object_datetime.year
        )

        actual_date = DateFormatter.format_date_bst(object_datetime, DATE_FORMAT)

        self.assertEqual(actual_date, expected_date)

from unittest import TestCase
from datetime import datetime
from maintain_frontend.services.validation.fieldset_validator import FieldsetValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder

VALID_FIELD_NAME = 'some field name'
VALID_DISPLAY_NAME = 'some display name'
VALID_DATA = 'some data'
EMPTY_STRING = ''
VALID_DAY = '12'
VALID_MONTH = '12'
VALID_PAST_YEAR = '1988'
VALID_FUTURE_YEAR = '5000'
CURRENT_DAY = datetime.now().day
CURRENT_MONTH = datetime.now().month
CURRENT_YEAR = datetime.now().year
VALID_FIELD_SET = [VALID_DATA, VALID_DATA, VALID_DATA]
INVALID_FIELD_SET = ''


class TestFieldsetValidator(TestCase):
    def test_is_required_with_valid_input(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator(VALID_FIELD_SET, VALID_FIELD_NAME, VALID_DISPLAY_NAME, validation_error_builder) \
            .is_required()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_required_with_invalid_input(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator(INVALID_FIELD_SET, VALID_FIELD_NAME, VALID_DISPLAY_NAME, validation_error_builder) \
            .is_required()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

    def test_has_enough_fields_populated_true(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DATA, VALID_DATA, VALID_DATA, EMPTY_STRING], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .has_enough_fields_populated(2)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_has_enough_fields_populated_false(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DATA, EMPTY_STRING, EMPTY_STRING, EMPTY_STRING], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .has_enough_fields_populated(2)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

    def test_has_enough_fields_populated_equal(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DATA, VALID_DATA, EMPTY_STRING, EMPTY_STRING], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .has_enough_fields_populated(2)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_valid_date_adds_error_when_date_invalid(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_valid_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

    def test_is_valid_date_does_not_add_error_when_date_valid(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH, VALID_PAST_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_valid_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_past_date_with_past_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH, VALID_PAST_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_past_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_past_date_with_future_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH, VALID_FUTURE_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_past_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

    def test_is_past_date_with_current_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_past_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_future_date_with_future_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH, VALID_FUTURE_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_future_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)
        self.assertTrue(VALID_FIELD_NAME not in validation_errors)

    def test_is_future_date_with_past_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([VALID_DAY, VALID_MONTH, VALID_PAST_YEAR], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_future_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

    def test_is_future_date_with_current_date(self):
        validation_error_builder = ValidationErrorBuilder()
        FieldsetValidator([CURRENT_DAY, CURRENT_DAY, CURRENT_DAY], VALID_FIELD_NAME, VALID_DISPLAY_NAME,
                          validation_error_builder) \
            .is_future_date()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertTrue(VALID_FIELD_NAME in validation_errors)

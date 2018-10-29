from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder
from maintain_frontend.services.validation.field_validator import FieldValidator
from unittest import TestCase

TEST_FIELD_NAME = 'testfieldname'
TEST_FIELD_NAME_2 = 'testfieldname2'
TEST_DISPLAY_NAME = 'TestDisplayName'
TEST_MESSAGE = 'is required'
TEST_INLINE = 'inline message'
TEST_HEADING = 'test heading message'
TEST_SUMMARY = 'test summary message'
TEST_EXPLANATORY = 'test explanatory text'
TEST_EXPECTED_MESSAGE = '{} {}'.format(
    TEST_DISPLAY_NAME,
    TEST_MESSAGE
)


class TestValidationErrorBuilder(TestCase):
    def test_error_is_added_given_empty_dict(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator = FieldValidator('dummy value', TEST_FIELD_NAME, TEST_DISPLAY_NAME, validation_error_builder)

        validation_error_builder.add_error(field_validator, TEST_EXPECTED_MESSAGE)

        validation_errors = validation_error_builder.get()

        self.assertIsNotNone(validation_errors.errors[TEST_FIELD_NAME])
        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.errors[TEST_FIELD_NAME].summary_message, TEST_EXPECTED_MESSAGE)

    def test_error_is_added_given_nonempty_dict(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator(
            'dummy value', TEST_FIELD_NAME, TEST_DISPLAY_NAME, validation_error_builder
        )
        field_validator_2 = FieldValidator(
            'dummy value', TEST_FIELD_NAME_2, TEST_DISPLAY_NAME, validation_error_builder
        )

        default_message = '{} {}'.format(
            TEST_DISPLAY_NAME,
            TEST_MESSAGE
        )
        validation_error_builder.add_error(field_validator_1, default_message)
        validation_error_builder.add_error(field_validator_2, default_message)

        validation_errors = validation_error_builder.get().errors
        self.assertEqual(len(validation_errors), 2)
        self.assertTrue(TEST_FIELD_NAME in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME].summary_message, default_message)

        self.assertEqual(validation_errors[TEST_FIELD_NAME].inline_message, default_message)

        self.assertTrue(TEST_FIELD_NAME_2 in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].summary_message, default_message)

        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].inline_message, default_message)

    def test_error_is_added_given_empty_display(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator('dummy value', TEST_FIELD_NAME, None, validation_error_builder)
        field_validator_2 = FieldValidator('dummy value', TEST_FIELD_NAME_2, None, validation_error_builder)

        validation_error_builder.add_error(field_validator_1, TEST_MESSAGE)
        validation_error_builder.add_error(field_validator_2, TEST_MESSAGE)

        validation_errors = validation_error_builder.get().errors
        self.assertEqual(len(validation_errors), 2)
        self.assertTrue(TEST_FIELD_NAME in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME].summary_message, TEST_MESSAGE)
        self.assertEqual(validation_errors[TEST_FIELD_NAME].inline_message, TEST_MESSAGE)
        self.assertTrue(TEST_FIELD_NAME_2 in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].summary_message, TEST_MESSAGE)
        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].inline_message, TEST_MESSAGE)

    def test_error_is_added_with_inline_message(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator('dummy value', TEST_FIELD_NAME,
                                           None,
                                           validation_error_builder,
                                           inline_message=TEST_INLINE)
        field_validator_2 = FieldValidator('dummy value', TEST_FIELD_NAME_2,
                                           None,
                                           validation_error_builder,
                                           inline_message=TEST_INLINE)

        validation_error_builder.add_error(field_validator_1, TEST_MESSAGE)
        validation_error_builder.add_error(field_validator_2, TEST_MESSAGE)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 2)
        self.assertTrue(TEST_FIELD_NAME in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME].summary_message, TEST_MESSAGE)

        self.assertEqual(validation_errors[TEST_FIELD_NAME].inline_message, TEST_INLINE)
        self.assertTrue(TEST_FIELD_NAME_2 in validation_errors)
        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].summary_message, TEST_MESSAGE)
        self.assertEqual(validation_errors[TEST_FIELD_NAME_2].inline_message, TEST_INLINE)

    def test_heading_message_added(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator('dummy value', TEST_FIELD_NAME, None,
                                           validation_error_builder,
                                           summary_heading_text=TEST_HEADING)

        validation_error_builder.add_error(field_validator_1, TEST_MESSAGE)

        validation_errors = validation_error_builder.get()
        self.assertEqual(validation_errors.summary_heading_text, TEST_HEADING)

    def test_summary_message_added(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator('dummy value', TEST_FIELD_NAME, None,
                                           validation_error_builder,
                                           summary_message=TEST_SUMMARY)

        validation_error_builder.add_error(field_validator_1, TEST_MESSAGE)

        validation_errors = validation_error_builder.get()
        self.assertEqual(validation_errors.errors[TEST_FIELD_NAME].summary_message, TEST_SUMMARY)

    def test_explanatory_text_added(self):
        validation_error_builder = ValidationErrorBuilder()
        field_validator_1 = FieldValidator('dummy value', TEST_FIELD_NAME, None,
                                           validation_error_builder,
                                           explanatory_text=TEST_EXPLANATORY)

        validation_error_builder.add_error(field_validator_1, TEST_MESSAGE)

        validation_errors = validation_error_builder.get()
        self.assertEqual(validation_errors.errors[TEST_FIELD_NAME].explanatory_text, TEST_EXPLANATORY)

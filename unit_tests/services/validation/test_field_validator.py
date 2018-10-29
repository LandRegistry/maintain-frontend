from unittest import TestCase
from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder

VALID_PHONE = '01234 567890'
INVALID_PHONE_NON_NUMERIC = 'test'
INVALID_PHONE_DASH = '01234-567890'
NINE_CHARS = '9 chars..'
TEN_CHARS = '10 chars..'
ELEVEN_CHARS = '11 chars...'
OVERWRITE_MESSAGE = 'Test overwrite message'


class TestFieldValidator(TestCase):
    def test_is_required_adds_error_when_input_empty(self):
        validation_error_builder = ValidationErrorBuilder()
        username = ''

        FieldValidator(username, 'username', 'Username',
                       validation_error_builder) \
            .is_required()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(validation_errors['username'].summary_message,
                         'Username is required')

    def test_is_required_doesnt_add_error_when_input_provided(self):
        validation_error_builder = ValidationErrorBuilder()
        username = 'TestUser'

        FieldValidator(username, 'username', 'Username',
                       validation_error_builder) \
            .is_required()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' not in validation_errors)

    def test_is_email_adds_error_when_email_invalid(self):
        validation_error_builder = ValidationErrorBuilder()
        email = 'invalid email'

        FieldValidator(email, 'email', email, validation_error_builder) \
            .is_email()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(validation_errors['email'].summary_message,
                         'invalid email is not a valid email address')

    def test_is_less_than_length_short_value(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(NINE_CHARS, 'username', 'Username',
                       validation_error_builder) \
            .is_length_less_than_or_equal_to(10)
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' not in validation_errors)

    def test_is_less_than_length_long_value(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(ELEVEN_CHARS, 'username', 'Username',
                       validation_error_builder) \
            .is_length_less_than_or_equal_to(10)
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' in validation_errors)

    def test_is_less_than_length_same_value(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(TEN_CHARS, 'username', 'Username',
                       validation_error_builder) \
            .is_length_less_than_or_equal_to(10)
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' not in validation_errors)

    def test_is_length_equal_to_true(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(TEN_CHARS, 'username', 'Username',
                       validation_error_builder) \
            .is_length_equal_to(10)
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' not in validation_errors)

    def test_is_length_equal_to_false(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(TEN_CHARS, 'username', 'Username',
                       validation_error_builder) \
            .is_length_equal_to(9)
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('username' in validation_errors)

    def test_is_item_count_equal_to(self):
        list_set = [1, 2]
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(list_set, 'a', 'b',
                       validation_error_builder) \
            .is_item_count_equal_to(2)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 0)

    def test_is_item_count_equal_to_set_error(self):
        list_set = [1, 2]
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(list_set, 'a', 'b', validation_error_builder) \
            .is_item_count_equal_to(1)
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(len(validation_errors), 1)
        self.assertEqual('Only 1 b can be supplied', validation_errors['a'].summary_message)

    def test_is_phone_number_adds_error_when_phone_invalid_dash(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(INVALID_PHONE_DASH, 'phoneNumber', 'Phone number',
                       validation_error_builder) \
            .is_phone_number()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(validation_errors['phoneNumber'].summary_message,
                         'Phone number is not a valid phone number')

    def test_is_phone_number_adds_error_when_phone_invalid_non_numeric(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(INVALID_PHONE_NON_NUMERIC, 'phoneNumber', 'Phone number',
                       validation_error_builder) \
            .is_phone_number()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(validation_errors['phoneNumber'].summary_message,
                         'Phone number is not a valid phone number')

    def test_is_phone_number_doesnt_add_error_when_phone_valid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(VALID_PHONE, 'phoneNumber', 'Phone number',
                       validation_error_builder) \
            .is_phone_number()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('phoneNumber' not in validation_errors)

    def test_is_item_in_list_doesnt_add_error_when_valid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("abc", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_item_in_list(["abc"])
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' not in validation_errors)

    def test_is_item_in_list_does_add_error_when_invalid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("def", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_item_in_list(["abc"])
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' in validation_errors)

    def test_is_item_not_in_list_doesnt_add_error_when_valid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("abc", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_item_not_in_list(["def"])
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' not in validation_errors)

    def test_is_item_not_in_list_does_add_error_when_invalid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("def", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_item_not_in_list(["def"])
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' in validation_errors)

    def test_add_error_with_header_message(self):
        validation_error_builder = ValidationErrorBuilder()
        email = 'test'
        header_message = 'This is a header message'

        FieldValidator(email, 'email', 'Email',
                       validation_error_builder, summary_heading_text=header_message) \
            .is_email()
        validation_errors = validation_error_builder.get()

        self.assertEqual(len(validation_errors.errors), 1)
        self.assertEqual(validation_errors.summary_heading_text, header_message)

    def test_add_error_with_inline_message(self):
        validation_error_builder = ValidationErrorBuilder()
        email = 'test'
        inline_message = 'This is an inline message'

        FieldValidator(email, 'email', None,
                       validation_error_builder, inline_message=inline_message) \
            .is_email()
        validation_errors = validation_error_builder.get().errors

        self.assertEqual(validation_errors['email'].inline_message, inline_message)

    def test_is_positive_or_zero_doesnt_add_error_when_valid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("12345", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_positive_number_or_zero()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' not in validation_errors)

    def test_is_positive_or_zero_does_add_error_when_invalid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("-12345", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_positive_number_or_zero()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' in validation_errors)

    def test_is_int_doesnt_add_error_when_valid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("12345", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_int()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' not in validation_errors)

    def test_is_int_does_add_error_when_invalid(self):
        validation_error_builder = ValidationErrorBuilder()

        FieldValidator("123.5", 'testfield', 'Test Field',
                       validation_error_builder) \
            .is_int()
        validation_errors = validation_error_builder.get().errors

        self.assertTrue('testfield' in validation_errors)

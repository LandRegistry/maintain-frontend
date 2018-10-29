from unittest import TestCase
from maintain_frontend import main
from maintain_frontend.two_factor_authentication.validation.\
    two_factor_authentication_validator import TwoFactorAuthenticationValidator


class TestTwoFactorAuthenticationValidator(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    def test_two_factor_authentication_validator_valid(self):
        code = '12345'
        validation_error_builder = TwoFactorAuthenticationValidator.validate(code)

        self.assertFalse(validation_error_builder.errors)

    def test_two_factor_authentication_validator_invalid_letters(self):
        code = '1234A'
        validation_error_builder = TwoFactorAuthenticationValidator.validate(code)

        self.assertIn(
            'Invalid security code',
            validation_error_builder.errors['code'].summary_message
        )

    def test_two_factor_authentication_validator_invalid_too_short(self):
        code = '1234'
        validation_error_builder = TwoFactorAuthenticationValidator.validate(code)

        self.assertIn(
            'Invalid security code',
            validation_error_builder.errors['code'].summary_message
        )

    def test_two_factor_authentication_validator_invalid_too_long(self):
        code = '123456'
        validation_error_builder = TwoFactorAuthenticationValidator.validate(code)

        self.assertIn(
            'Invalid security code',
            validation_error_builder.errors['code'].summary_message
        )

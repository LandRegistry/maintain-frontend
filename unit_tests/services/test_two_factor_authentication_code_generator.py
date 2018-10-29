from unittest import TestCase
from maintain_frontend.services import two_factor_authentication_code_generator


class TestTwoFactorAuthenticationCodeGenerator(TestCase):

    def test_generate_code_different_numbers(self):
        code1 = two_factor_authentication_code_generator.generate_code()
        code2 = two_factor_authentication_code_generator.generate_code()
        self.assertNotEqual(code1, code2)

    def test_generate_code_5_digits(self):
        code = two_factor_authentication_code_generator.generate_code()
        self.assertEqual(len(str(code)), 5)

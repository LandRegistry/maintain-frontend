from maintain_frontend import main
from flask_testing import TestCase
from maintain_frontend.add_lon.validation.dominant_address_validator import DominantAddressValidator


class TestDominantAddressValidator(TestCase):
    def create_app(self):
        main.app.testing = True
        return main.app

    def setUp(self):
        main.app.config['Testing'] = True
        main.app.config['WTF_CSRF_ENABLED'] = False

    def test_validation_have_address_no_description(self):
        test_form = {'have_address': 'Yes', 'charge_geographic_description': ''}
        validation_error_builder = DominantAddressValidator.validate(test_form)

        self.assertFalse(validation_error_builder.errors)

    def test_validation_no_address_have_description(self):
        test_form = {'have_address': 'No', 'charge_geographic_description': 'The land near the test site'}
        validation_error_builder = DominantAddressValidator.validate(test_form)

        self.assertFalse(validation_error_builder.errors)

    def test_validation_no_address_no_description(self):
        test_form = {'have_address': 'No', 'charge_geographic_description': ''}
        validation_error_builder = DominantAddressValidator.validate(test_form)

        self.assertIn('Location is required',
                      validation_error_builder.errors['charge_geographic_description'].summary_message)

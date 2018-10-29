from unittest import TestCase
from maintain_frontend.llc1.validation.search_description_validator import SearchDescriptionValidator

VALID_DESCRIPTION = 'This is a search description'
BLANK_DESCRIPTION = ''
OVERLONG_DESCRIPTION = 'X' * 1001
MAX_LENGTH_DESCRIPTION = 'X' * 1000


class TestLLC1DescriptionValidator(TestCase):
    def test_description_valid_passes_when_no_single_address(self):
        result = SearchDescriptionValidator.validate(VALID_DESCRIPTION, 'No').errors
        self.assertEqual(len(result), 0)

    def test_description_max_length_passes__when_no_single_address(self):
        result = SearchDescriptionValidator.validate(MAX_LENGTH_DESCRIPTION, 'No').errors
        self.assertEqual(len(result), 0)

    def test_description_blank_fails__when_no_single_address(self):
        result = SearchDescriptionValidator.validate(BLANK_DESCRIPTION, 'No').errors
        self.assertEqual(len(result), 1)
        self.assertEqual(result['charge-geographic-description'].inline_message, "Explain where you want to search "
                                                                                 "without an address. For example, "
                                                                                 "use a nearby landmark as "
                                                                                 "a reference point. ")
        self.assertEqual(result['charge-geographic-description'].summary_message, "Describe the search area")

    def test_description_overlong_fails_when_no_single_address(self):
        result = SearchDescriptionValidator.validate(OVERLONG_DESCRIPTION, 'No').errors
        self.assertEqual(len(result), 1)
        self.assertEqual(result['charge-geographic-description'].inline_message, "Reduce your answer to 1000 "
                                                                                 "characters or less")
        self.assertEqual(result['charge-geographic-description'].summary_message, "Answer is too long")

    def test_no_radio_button_selected(self):
        result = SearchDescriptionValidator.validate(None, '').errors

        self.assertEqual(len(result), 1)
        self.assertEqual(result['address-from-group'].summary_message, 'Choose one option')

    def test_no_selected_address_when_single_address(self):
        result = SearchDescriptionValidator.validate(BLANK_DESCRIPTION, 'ProvideAddress').errors
        self.assertEqual(len(result), 1)

        self.assertEqual(result['search_term'].inline_message, "Search for a different postcode if the "
                                                               "address you need is not listed.")
        self.assertEqual(result['search_term'].summary_message, "Choose an address")

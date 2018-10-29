from unittest import TestCase
from maintain_frontend.add_land_charge.validation.authority_validator import AuthorityValidator

ORIGINATING_AUTHORITIES = [
    'Authority A',
    'Authority B',
    'Authority C',
    'Authority D',
]

VALID_AUTHORITY = 'Authority A'
PARTIAL_AUTHORITY = 'Auth A'
INVALID_AUTHORITY = ''


class TestAuthorityValidator(TestCase):

    def test_authority_in_list(self):
        result = AuthorityValidator.validate(VALID_AUTHORITY, ORIGINATING_AUTHORITIES).errors
        self.assertEqual(len(result), 0)

    def test_no_authority(self):
        result = AuthorityValidator.validate(INVALID_AUTHORITY, ORIGINATING_AUTHORITIES).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['authority-search-field'].summary_message,
            'Authority name is required'
        )
        self.assertEqual(
            result['authority-search-field'].inline_message,
            'Authority name is required'
        )

    def test_parital_authority(self):
        result = AuthorityValidator.validate(PARTIAL_AUTHORITY, ORIGINATING_AUTHORITIES).errors

        self.assertEqual(len(result), 1)
        self.assertEqual(
            result['authority-search-field'].summary_message,
            'No match found'
        )
        self.assertEqual(
            result['authority-search-field'].inline_message,
            'Try a different search'
        )

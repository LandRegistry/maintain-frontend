from enum import Enum
from unittest import TestCase
from maintain_frontend.services.field_utilities import get_ordered_edited_fields, has_value_changed


class TestFieldUtilities(TestCase):
    def test_has_value_changed_true(self):
        old_value = 1
        new_value = 2
        self.assertTrue(has_value_changed(old_value, new_value))

    def test_has_value_changed_false(self):
        old_value = 1
        new_value = 1
        self.assertFalse(has_value_changed(old_value, new_value))

    def test_get_ordered_edited_fields(self):
        class TestEnum(Enum):
            first = "one"
            second = "two"
            third = "three"
            fourth = "four"
            fifth = "five"

        edited_fields = [
            'fifth',
            'fourth',
            'first',
            'third',
            'second'
        ]

        result = get_ordered_edited_fields(edited_fields, TestEnum)

        self.assertEqual(result.index('first'), 0)
        self.assertEqual(result.index('second'), 1)
        self.assertEqual(result.index('third'), 2)
        self.assertEqual(result.index('fourth'), 3)
        self.assertEqual(result.index('fifth'), 4)

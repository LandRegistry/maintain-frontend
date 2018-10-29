from maintain_frontend.services.validation.field_validator import FieldValidator
from maintain_frontend.services.validation.validation_error_builder import ValidationErrorBuilder


class LandCompensationPaymentValidator(object):

    @staticmethod
    def validate(land_compensation_paid, amount_of_compensation, vary_action):
        """Specifies which validation methods should be called for each input field.


        parameters:
            - land_compensation_paid: Part of the compensation (paid in advance)
            - amount_of_compensation: The total amount of compensation payable
            to the landowner from which the land was acquired.

        returns:
            dict: An instance of ValidationErrorBuilder with a ValidationError dict and a heading summary message.
        """

        validation_error_builder = ValidationErrorBuilder()

        FieldValidator(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                       validation_error_builder, summary_message='Enter the advance payment',
                       inline_message='This is part of the compensation (paid in advance)') \
            .is_required()

        if not vary_action:
            FieldValidator(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount',
                           validation_error_builder, summary_message='Enter the total compensation',
                           inline_message='This is the total compensation') \
                .is_required()

            FieldValidator(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount',
                           validation_error_builder,
                           summary_message='Compensation must be a positive number',
                           inline_message='Compensation must be a positive number')\
                .is_positive_number()

            FieldValidator(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                           validation_error_builder,
                           summary_message='Advance payment cannot be more than total compensation',
                           inline_message='Advance payment cannot be more than total compensation')\
                .is_less_than_or_equal_to(amount_of_compensation)

            FieldValidator(amount_of_compensation, 'amount-of-compensation', 'Total compensation amount',
                           validation_error_builder,
                           summary_message='Compensation payment can only have 2 numbers after the decimal place',
                           inline_message='Compensation payment can only have 2 numbers after the decimal place')\
                .is_number_with_zero_or_x_decimal_places(2)

        FieldValidator(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                       validation_error_builder,
                       summary_message='Advance payment must be a positive number',
                       inline_message='Advance payment must be a positive number')\
            .is_positive_number()

        FieldValidator(land_compensation_paid, 'land-compensation-paid', 'Advance payment amount',
                       validation_error_builder,
                       summary_message='Advance payment can only have 2 numbers after the decimal place',
                       inline_message='Advance payment can only have 2 numbers after the decimal place')\
            .is_number_with_zero_or_x_decimal_places(2)

        return validation_error_builder.get()

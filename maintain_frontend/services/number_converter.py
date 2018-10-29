class NumberConverter(object):

    @staticmethod
    def format_number_string(value, leading_char='', trailing_char='', force_two_dp=False):
        """Remove spaces, remove specified leading and trailing characters, and clean number string to 2 d.p."""
        value = value.replace(' ', '')

        if leading_char and value and value[0] == leading_char:
            value = value[1:]

        if trailing_char and value and value[-1] == trailing_char:
            value = value[:-1]

        if force_two_dp:
            # this will class as invalid numeric values with more than 2 non-zero dp
            if '.' in value:
                # dp is all decimal places after the first 2
                dp = value.split('.')[-1][2:]
                if dp:
                    try:
                        dp_int = int(dp)
                        if dp_int != 0:
                            return value
                    except ValueError:
                        return value

        try:
            if "e" in value:
                # This is required because exponents will pass the float cast (e.g. "1e10")
                return value

            new_value = float(value)
            if force_two_dp:
                return "{0:.2f}".format(new_value)
            else:
                return value
        except ValueError:
            return value

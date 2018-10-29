class AddressConverter(object):

    @staticmethod
    def to_charge_address(address):
        return {
            'line-1': address['line_1'],
            'line-2': address['line_2'],
            'line-3': address['line_3'],
            'line-4': address['line_4'],
            'line-5': address['line_5'],
            'line-6': address['line_6'],
            'postcode': address['postcode'],
            'unique-property-reference-number': address['uprn']
        }

    @staticmethod
    def get_display_address(charge_address):
        display_address = charge_address['line-1']
        if 'line-2' in charge_address and charge_address['line-2']:
            display_address += ", " + charge_address['line-2']
        if 'line-3' in charge_address and charge_address['line-3']:
            display_address += ", " + charge_address['line-3']
        if 'line-4' in charge_address and charge_address['line-4']:
            display_address += ", " + charge_address['line-4']
        if 'line-5' in charge_address and charge_address['line-5']:
            display_address += ", " + charge_address['line-5']
        if 'line-6' in charge_address and charge_address['line-6']:
            display_address += ", " + charge_address['line-6']

        display_address += " " + charge_address['postcode']
        return display_address

    @staticmethod
    def condense_address(address_form):
        """Remove any lines in the address that are left empty and convert to session format"""
        address_dict = {'country': address_form.get('country', '')}

        address_list = []

        # Loop through all address fields and add non-blank lines to list
        for i in range(6):
            value = address_form['address_line_{}'.format(i + 1)]
            if value:
                address_list.append(value)

        # Loop through list and create new lines for session for each
        for i in range(len(address_list)):
            key = 'line-{}'.format(i + 1)
            address_dict[key] = address_list[i]

        if 'postcode' in address_form:
            address_dict['postcode'] = address_form.get('postcode', '').upper()

        return address_dict

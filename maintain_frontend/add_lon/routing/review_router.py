from flask import g, url_for, current_app


class ReviewRouter(object):

    @staticmethod
    def get_redirect_url(default_route):
        """Return the url for redirect_route in session if it has been set, or the url for the default_route otherwise.


        - default_route: The route to return the URL of if the redirect_url is not set.
        :return: The url of session.redirect_route if set, or the url of the given route otherwise.
        """
        redirect_route = g.session.redirect_route
        redirect_url = url_for(default_route)
        if redirect_route:
            redirect_url = url_for(redirect_route)

        current_app.logger.info('Returning redirect URL: {}'.format(redirect_url))
        return redirect_url

    @staticmethod
    def update_edited_field(field, value):
        """Adds the field to edited_fields if the value in session and the given values are different.


        - field: A field to look up in the add charge state.
        - value: The value to test the field against.
        """
        if g.session.redirect_route and value != getattr(g.session.add_lon_charge_state, field):
            current_app.logger.info('Adding {} field to edited_fields'.format(field))
            g.session.edited_fields[field] = field
            g.session.commit()

    @staticmethod
    def update_edited_dominant_address(field, value):
        """Adds the field to edited_fields if the value in session and the given values are different.

           Checks charge_address and charge_geographic_description as only one can be entered, so removes

           the other value from edited fields list.


        - field: A field to look up in the add charge state.
        - value: The value to test the field against.
        """
        if g.session.redirect_route and value != getattr(g.session.add_lon_charge_state, field):
            if field == 'charge_geographic_description' and 'charge_address' in g.session.edited_fields:
                del g.session.edited_fields['charge_address']
            elif field == 'charge_address' and 'charge_geographic_description' in g.session.edited_fields:
                del g.session.edited_fields['charge_geographic_description']

            current_app.logger.info('Adding {} field to edited_fields'.format(field))
            g.session.edited_fields[field] = field
            g.session.commit()

    @staticmethod
    def update_edited_height_or_position(value):
        """Adds the height or position to edited_fields if the value in session and the given values are different.


        - value: The updated position_and_dimension dict to compare against session
        """
        if g.session.redirect_route:
            sess_pos = getattr(g.session.add_lon_charge_state, 'structure_position_and_dimension')

            if value['height'] != sess_pos['height'] or \
                    ('units' in value and 'units' in sess_pos and value['units'] != sess_pos['units']):
                current_app.logger.info('Adding servient_height field to edited_fields')
                g.session.edited_fields['servient_height'] = 'servient_height'
                g.session.commit()

            if value['extent-covered'] != sess_pos['extent-covered'] or \
                    ('part-explanatory-text' in value and 'part-explanatory-text' in sess_pos and
                        value['part-explanatory-text'] != sess_pos['part-explanatory-text']):
                current_app.logger.info('Adding servient_position field to edited_fields')
                g.session.edited_fields['servient_position'] = 'servient_position'
                g.session.commit()

    @staticmethod
    def update_edited_filename_field(value):
        """Adds the individual filename to edited_fields if the value in session and the given values are different.


        - value: The value to test the field against.
        """
        if g.session.redirect_route:
            if value['form_a'] != getattr(g.session, 'filenames')['form_a']:
                current_app.logger.info('Adding form_a_file field to edited_fields')
                g.session.edited_fields['form_a_file'] = 'form_a_file'
                g.session.commit()
            if value['temporary_lon_cert'] != getattr(g.session, 'filenames')['temporary_lon_cert']:
                if value['temporary_lon_cert'] == '':
                    ReviewRouter.remove_from_edited_fields('temporary_lon_file')
                else:
                    current_app.logger.info('Adding temporary_lon_file field to edited_fields')
                    g.session.edited_fields['temporary_lon_file'] = 'temporary_lon_file'
                g.session.commit()
            if value['definitive_lon_cert'] != getattr(g.session, 'filenames')['definitive_lon_cert']:
                if value['definitive_lon_cert'] == '':
                    ReviewRouter.remove_from_edited_fields('definitive_lon_file')
                else:
                    current_app.logger.info('Adding definitive_lon_file field to edited_fields')
                    g.session.edited_fields['definitive_lon_file'] = 'definitive_lon_file'
                g.session.commit()

    @staticmethod
    def remove_from_edited_fields(field):
        if field in g.session.edited_fields:
            current_app.logger.info('Removing {} field from edited_fields'.format(field))
            del g.session.edited_fields[field]

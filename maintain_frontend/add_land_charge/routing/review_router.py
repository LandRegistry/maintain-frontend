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

        if g.session.redirect_route and value != getattr(g.session.add_charge_state, field):
            current_app.logger.info('Adding {} field to edited_fields'.format(field))
            g.session.edited_fields.append(field)
            g.session.commit()

    @staticmethod
    def remove_edited_field(field):
        """Removes the field to edited_fields if the value in session


        - field: A field to look up in the add charge state.
        """

        if g.session.redirect_route and getattr(g.session.add_charge_state, field):
            current_app.logger.info('Removing {} field to edited_fields'.format(field))
            if field in g.session.edited_fields:
                g.session.edited_fields.remove(field)
                g.session.commit()

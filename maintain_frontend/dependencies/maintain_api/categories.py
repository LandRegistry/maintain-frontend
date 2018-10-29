from flask import current_app, g
from maintain_frontend.exceptions import ApplicationError
from maintain_frontend.models import Category, SubCategory
from maintain_frontend.config import MAINTAIN_API_URL


class CategoryService(object):
    """Service class for making requests to category and stat prov endpoints."""

    @staticmethod
    def get_categories():
        request_path = "{0}/categories".format(MAINTAIN_API_URL)
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code != 200:
            current_app.logger.warning(
                'Failed to retrieve top level categories with status code {}'.format(response.status_code))
            raise ApplicationError('Failed to retrieve top level categories')

        categories = []
        for category in response.json():
            if category['permission'] is not None:
                if category['permission'] in g.session.user.permissions:
                    categories.append(
                        {
                            "display": category['display-name'],
                            "name": category['name']
                        })
            else:
                categories.append(
                    {
                        "display": category['display-name'],
                        "name": category['name']
                    })

        return categories

    @staticmethod
    def get_category_parent_info(category):
        request_path = "{0}/categories/{1}".format(MAINTAIN_API_URL, category)
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code != 200:
            current_app.logger.warning(
                'Failed to retrieve sub categories with status code {}'.format(response.status_code))
            raise ApplicationError('Failed to retrieve sub categories')

        category_details = response.json()

        return Category(category_details["name"],
                        category_details["display-name"],
                        CategoryService.filter_categories_by_permissions(category_details["sub-categories"]),
                        category_details["statutory-provisions"],
                        category_details["instruments"],
                        None
                        )

    @staticmethod
    def get_sub_category_info(category, sub_category):
        request_path = "{0}/categories/{1}/sub-categories/{2}".format(
            MAINTAIN_API_URL, category, sub_category)
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code != 200:
            current_app.logger.warning(
                'Failed to retrieve sub categories with status code {}'.format(response.status_code))
            raise ApplicationError('Failed to retrieve sub categories')

        category_details = response.json()

        return Category(category_details["name"],
                        category_details["display-name"],
                        CategoryService.filter_categories_by_permissions(category_details["sub-categories"]),
                        category_details["statutory-provisions"],
                        category_details["instruments"],
                        category_details["parent"]
                        )

    @staticmethod
    def get_all_stat_provs():
        request_path = "{0}/statutory-provisions".format(MAINTAIN_API_URL)
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        response = g.requests.get(request_path, params={'selectable': True})

        if response.status_code != 200:
            current_app.logger.warning(
                'Failed to retrieve statutory provisions with status code {}'.format(response.status_code))
            raise ApplicationError('Failed to retrieve statutory provisions')

        return response.json()

    @staticmethod
    def get_all_instruments():
        request_path = "{0}/instruments".format(MAINTAIN_API_URL)
        current_app.logger.info("Calling search api via this URL: %s", request_path)

        response = g.requests.get(request_path)

        if response.status_code != 200:
            current_app.logger.warning(
                'Failed to retrieve instruments with status code {}'.format(response.status_code))
            raise ApplicationError('Failed to retrieve instruments')

        return response.json()

    @staticmethod
    def filter_categories_by_permissions(categories_to_be_filtered):
        categories = []
        for category in categories_to_be_filtered:
            if category['permission'] is not None:
                if category['permission'] in g.session.user.permissions:
                    categories.append(SubCategory(category['name'], category['display-name']))
            else:
                categories.append(SubCategory(category['name'], category['display-name']))

        return categories

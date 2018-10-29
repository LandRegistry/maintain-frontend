import datetime
import pytz


class DateFormatter(object):

    @staticmethod
    def to_iso_format(day, month, year):
        """Formats a date into the ISO format (YYYY MM DD).


        This is the format required for storage into the database.
        """
        if day and month and year:
            return datetime.date(
                int(year),
                int(month),
                int(day)
            ).isoformat()

    @staticmethod
    def to_display_format(day, month, year):
        """Formats a date into DD MM YYYY format.


        This is the format required for display.
        """
        if day and month and year:
            return datetime.date(
                int(year),
                int(month),
                int(day)
            ).strftime("%d-%m-%Y")

    @staticmethod
    def format_date_bst(date, date_format):
        object_datetime_utc = date.replace(tzinfo=pytz.utc)
        localised_date = object_datetime_utc.astimezone(pytz.timezone('Europe/London'))

        return localised_date.strftime(date_format)

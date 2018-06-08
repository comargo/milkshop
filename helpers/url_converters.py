import datetime

import django.urls


class IsoDateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    @staticmethod
    def to_python(value):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    @staticmethod
    def to_url(value):
        assert isinstance(value, datetime.date)
        return value.isoformat()


django.urls.register_converter(IsoDateConverter, 'date')

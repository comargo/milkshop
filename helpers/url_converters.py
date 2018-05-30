import datetime

from django.urls import register_converter


class IsoDateConverter:
    regex = '[0-9]{4}-[0-9]{2}-[0-9]{2}'

    def to_python(self, value):
        try:
            return datetime.datetime.strptime(value, "%Y-%m-%d").date()
        except ValueError:
            return None

    def to_url(self, value):
        assert isinstance(value, datetime.date)
        return value.isoformat()


register_converter(IsoDateConverter, 'date')

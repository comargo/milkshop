from copy import copy

from django.template import Template, Context
from django.test import TestCase, override_settings

invalid_string = "invalid_string"


@override_settings(TEMPLATE_STRING_IF_INVALID=invalid_string)
class HelpersTesttCase(TestCase):
    context = Context({
        "dict_value": {key: f'{key}_value' for key in ["a", "b"]},
        "list_value": [f'{key}_value' for key in range(2)],
        "tuple_value": tuple(f'{key}_value' for key in range(2)),
    })

    def test_key_dict_const_valid(self):
        template = Template(r"""{% load helpers %}{{ dict_value | key:"a" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, context["dict_value"]["a"])

    def test_key_dict_const_invalid(self):
        template = Template(r"""{% load helpers %}{{ dict_value | key:"c" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

    def test_key_dict_var_valid(self):
        template = Template(r"""{% load helpers %}{{ dict_value | key:a }}""")
        context = copy(self.context)
        context["a"] = "b"
        rendered = template.render(context)
        self.assertEqual(rendered, context["dict_value"]["b"])

    def test_key_dict_var_invalid(self):
        template = Template(r"""{% load helpers %}{{ dict_value | key:a }}""")
        context = copy(self.context)
        context["a"] = "c"
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

    def test_key_list_const_valid(self):
        template = Template(r"""{% load helpers %}{{ list_value | key:"0" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, context["list_value"][0])

    def test_key_list_const_invalid(self):
        template = Template(r"""{% load helpers %}{{ list_value | key:"3" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

    def test_key_list_var_valid(self):
        template = Template(r"""{% load helpers %}{{ list_value | key:a }}""")
        context = copy(self.context)
        context["a"] = 1
        rendered = template.render(context)
        self.assertEqual(rendered, context["list_value"][1])

    def test_key_list_var_invalid(self):
        template = Template(r"""{% load helpers %}{{ list_value | key:a }}""")
        context = copy(self.context)
        context["a"] = 3
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

    def test_key_tuple_const_valid(self):
        template = Template(r"""{% load helpers %}{{ tuple_value | key:"0" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, context["tuple_value"][0])

    def test_key_tuple_const_invalid(self):
        template = Template(r"""{% load helpers %}{{ tuple_value | key:"3" }}""")
        context = copy(self.context)
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

    def test_key_tuple_var_valid(self):
        template = Template(r"""{% load helpers %}{{ tuple_value | key:a }}""")
        context = copy(self.context)
        context["a"] = 1
        rendered = template.render(context)
        self.assertEqual(rendered, context["tuple_value"][1])

    def test_key_tuple_var_invalid(self):
        template = Template(r"""{% load helpers %}{{ tuple_value | key:a }}""")
        context = copy(self.context)
        context["a"] = 3
        rendered = template.render(context)
        self.assertEqual(rendered, invalid_string)

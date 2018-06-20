class ViewTestCaseMixin:
    view_class = None
    template_name = None

    # noinspection PyPep8Naming
    def setUp(self):
        self.assertIsNotNone(self.view_class, "Error in test case setup")
        self.assertIsNotNone(self.template_name, "Error in test case setup")

    def test_viewclass(self, response=None):
        response = response or self.get_response()
        self.assertIsNotNone(response, "Error in test case setup")
        self.assertIsInstance(response.context['view'], self.view_class)

    def test_status_code(self, response=None):
        response = response or self.get_response()
        self.assertIsNotNone(response, "Error in test case setup")
        self.assertEqual(200, response.status_code)

    def test_template(self, response=None):
        response = response or self.get_response()
        self.assertTemplateUsed(response, self.template_name)

    def get_response(self):
        self.fail("No GET response provided")

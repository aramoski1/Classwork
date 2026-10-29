
from django.test import TestCase
from django.http import HttpRequest
from .views import home_page


class HomePageTest(TestCase):

    def test_home_page_returns_correct_html(self):
        request = HttpRequest()
        response = home_page(request)

        self.assertTrue(
            response.content.startswith(b"<html>")
        )
        self.assertIn(
            b"<title>To-Do Lists</title>",
            response.content
        )
        self.assertTrue(
            response.content.endswith(b"</html>")
        )

    def test_root_url_resolves_to_home_page(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"To-Do Lists", response.content)

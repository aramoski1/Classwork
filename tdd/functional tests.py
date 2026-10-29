
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import unittest


class NewVisitorTest(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_can_start_a_list(self):
        # User visits the homepage
        self.browser.get("http://localhost:8000")

        # Page title contains To-Do
        self.assertIn("To-Do", self.browser.title)

        # There is a To-Do heading
        header = self.browser.find_element(By.TAG_NAME, "h1")
        self.assertIn("To-Do", header.text)

        # There is an input box
        inputbox = self.browser.find_element(By.ID, "id_new_item")
        self.assertEqual(
            inputbox.get_attribute("placeholder"),
            "Enter a to-do item"
        )

        # User types a new item
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)

        # User should see the item in the table
        table = self.browser.find_element(By.ID, "id_list_table")
        rows = table.find_elements(By.TAG_NAME, "tr")

        self.assertTrue(
            any("1: Buy milk" in row.text for row in rows),
            "New item did not appear in the table"
        )


if __name__ == "__main__":
    unittest.main()

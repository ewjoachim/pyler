import unittest
import os
import tempfile
import json

from pyler.website import Website

from pyler.utils import answers


class AutomaticTest(object):
    os.environ["AUTOMATIC"] = "1"


class WebsiteTests(unittest.TestCase):

    def get_website(self):
        website = Website()
        website.renew_session()
        return website

    def setUp(self):
        self.conf = tempfile.NamedTemporaryFile()
        os.environ["PYLER_CONF"] = self.conf.name

    def tearDown(self):
        try:
            self.conf.close()
        except IOError:
            pass

    def get_real_credentials(self):
        dir_name = os.path.dirname(__file__)
        file_name = "test.conf.json"
        try:
            with open(os.path.join(dir_name, file_name), "r") as handler:
                return json.load(handler)
        except IOError:
            raise unittest.skipTest(
                "For all tests implying a real connection to the Project Euler "
                "website, please create a file named {} in {} which is a json "
                "file containing something like : "
                """{"username": "yay", "password": "ohoho"}"""
            )

    def prepare_connection(self):
        credentials = self.get_real_credentials()
        self.prepare_answers([credentials["username"], credentials["password"]])

    def prepare_answers(self, prepared_answers):
        answers.extend(prepared_answers)

    def test_get_problem_content(self):
        website = self.get_website()
        self.assertIn("If we list all the natural numbers", website.get_problem_content(1))

    def test_connect_no_id(self):
        website = self.get_website()
        with self.assertRaises(ValueError) as exc:
            self.prepare_answers(["", ""])
            website.connect()
        self.assertIn("Cannot connect without credentials", str(exc.exception))

    def test_connect_bad_cred(self):
        website = self.get_website()
        with self.assertRaises(ValueError) as exc:
            self.prepare_answers(["hoho", "haha"])
            website.connect()
        self.assertIn("Unsuccessful login", str(exc.exception))

    def test_connect_good_cred(self):
        website = self.get_website()
        self.prepare_connection()
        website.connect()

    def test_check_solution_good_read(self):
        website = self.get_website()
        self.prepare_connection()
        self.assertTrue(website.check_solution(1, 233168, "read_only"))

    def test_check_solution_good_submit(self):
        website = self.get_website()
        self.prepare_connection()
        self.assertTrue(website.check_solution(1, 233168, "submit_only"))

    def test_check_solution_bad_read(self):
        website = self.get_website()
        self.prepare_connection()
        self.assertFalse(website.check_solution(1, 233169, "read_only"))

    def test_check_solution_bad_submit(self):
        website = self.get_website()
        self.prepare_connection()
        self.assertFalse(website.check_solution(1, 233169, "submit_only"))

from os import path
import tempfile
import itertools
import pickle
import base64

from bs4 import BeautifulSoup
import requests

from .config import Config
from .utils import default_open


class Website():
    base_url = "https://projecteuler.net"
    _session = None
    captcha_tries = 3

    class NoCredentials(Exception):
        pass

    def get_problem_content(self, problem_id):

        response = self.get(problem_id)
        if response.status_code != 200:
            raise ValueError("Cannot access the problem")

        soup = self.soup(response)
        return soup.select_one("div.problem_content").get_text().strip()

    def connect(self):
        credentials = Config().get_or_ask_for_credentials()
        credentials.update({
            "sign_in": "Sign In",
            "remember_me": "1",
        })
        if not all(credentials.values()):
            raise ValueError("Cannot connect without credentials")
        soup = self.captcha(
            reason="Connection Captcha",
            post_data=credentials,
            url=self.url(url_path="sign_in")
        )
        if "Sign in successful" not in soup.select_one("#message").get_text():
            raise ValueError("Unsuccessful login :(")

        config_parser = Config()
        config_parser.write_elements(
            session=base64.b64encode(pickle.dumps(self._session.cookies)).decode("ascii")
        )

    @property
    def session(self):
        session = self.__class__._session
        if not session:
            session = self.__class__._session = requests.Session()
            config_parser = Config()
            config = config_parser.get_config()
            config_session = config["session"]
            if config_session:
                session.cookies = pickle.loads(base64.b64decode(config_session))

        return session

    def url(self, problem_id=None, url_path=None):
        """
        Generates the URL either with a problem id or
        a path on the domain.
        """
        if problem_id:
            url_path = "problem={}".format(problem_id)
        return path.join(self.base_url, url_path)

    def get(self, *args, **kwargs):
        """
        Calls a GET url
        """
        return self.session.get(self.url(*args, **kwargs))

    def captcha(self, reason, post_data, url):
        """
        Completes the Captcha challenge (by forwarding it to the user)
        """
        for __ in range(self.captcha_tries):

            print(reason)
            captcha = self.get(url_path="captcha/show_captcha.php")
            with tempfile.NamedTemporaryFile() as image_captcha:
                image_captcha.write(captcha.content)
                image_captcha.flush()
                default_open(image_captcha.name)
                captcha_attempt = input("Can you read this for me please ? (should be 5 numbers) : ")

            post_data["captcha"] = captcha_attempt

            response = self.session.post(url, data=post_data)
            soup = self.soup(response)
            message = soup.select_one("#message")
            if message and "confirmation code" in message.get_text():
                print("Invalid captcha !")
                continue
            else:
                return soup
        raise ValueError("You suck at captcha. Are you even TRYING to pass as a human or ...?")

    def soup(self, response):
        return BeautifulSoup(response.content, 'html.parser')

    def check_solution(self, problem_id, solution, method=None):
        """
        Check that a solution for a given problem is correct, either
        by reading the html page if we already cleared it or by
        submitting it.
        method can restrain the search method to one of the 2 solutions :
        use "read_only" or "submit_only
        """
        response = self.session.get(self.url(problem_id))
        soup = self.soup(response)

        info_panel = soup.select_one("#info_panel > div")
        if not info_panel or "Logged in as" not in info_panel.get_text():
            self.connect()
            response = self.session.get(self.url(problem_id))
            soup = self.soup(response)

        already_found = soup.find(string="Answer:")

        if already_found and method != "submit_only":
            good_solution = list(itertools.islice(already_found.next_elements, 1, 2))[0].find("b").string
            return "{}".format(solution) == good_solution

        if method != "read_only":

            soup = self.captcha(
                reason="Solution Check Captcha",
                post_data={"guess_{}".format(problem_id): solution},
                url=self.url(problem_id=problem_id)
            )
            text = soup.select_one("#content").get_text()

            if "appears to be incorrect" in text:
                return False
            elif "is correct" in text:
                return True

        raise ValueError("Cannot determine whether it is a success or a failure.")

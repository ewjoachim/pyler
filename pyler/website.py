import base64
import pickle
import urllib
import tempfile

from bs4 import BeautifulSoup
import requests

from .config import Config
from . import utils


class Website(object):
    base_url = "https://projecteuler.net"
    _session = None
    captcha_tries = 3

    class NoCredentials(Exception):
        pass

    @property
    def session(self):
        if not self._session:
            self._session = requests.Session()
            config = Config()

            load_session_cookies(config, self._session)

        return self._session

    def renew_session(self):
        if hasattr(self, "_session"):
            self._session = None

        config = Config()
        config["session"] = None


def get_message(soup):
    try:
        return soup.select_one("#message").get_text()
    except AttributeError:
        return ""


def get_problem_content(website, problem_id):

    response = request_get(website, problem_id)
    soup = get_soup(response)

    message = get_message(soup)

    if message == "Problem not accessible":
        raise ValueError("Cannot access the problem")

    return soup.select_one("div.problem_content").get_text().strip()


def connect(website):
    config = Config()
    credentials = config.get_or_ask_for_credentials()
    print(credentials)
    credentials.update({
        "sign_in": "Sign In",
        "remember_me": "1",
    })
    if not all(credentials.values()):
        raise ValueError("Cannot connect without credentials")

    soup = solve_captcha(
        website=website,
        reason="Connection Captcha",
        post_data=credentials,
        url=get_url(website, url_path="sign_in")
    )
    if "Sign in successful" not in get_message(soup):
        raise ValueError("Unsuccessful login :(")

    save_session_cookies(config, website.session)


def load_session_cookies(config, session):
    config_session = config["session"]
    if config_session:
        session.cookies = pickle.loads(base64.b64decode(config_session))


def save_session_cookies(config, session):
    config["session"] = base64.b64encode(pickle.dumps(
        session.cookies)).decode("ascii")


def get_url(website, problem_id=None, url_path=None):
    """
    Generates the URL either with a problem id or
    a path on the domain.
    """
    if problem_id:
        url_path = "problem={}".format(problem_id)
    return urllib.parse.urljoin(website.base_url, url_path)


def request_get(website, *args, **kwargs):
    """
    Calls a GET url. Arguments include those of the url method, and
    needs_connection (True or False) that determine if a Connection
    will be attempted if we detect the session is no longer valid.
    """
    needs_connection = kwargs.pop("needs_connection", False)

    response = website.session.get(get_url(website, *args, **kwargs))
    soup = get_soup(response)

    info_panel = soup.select_one("#about_page")
    if info_panel:
        website.renew_session()
        if needs_connection:
            connect(website)
        response = website.session.get(get_url(website, *args, **kwargs))
    return response


def solve_captcha(website, reason, post_data, url):
    """
    Completes the Captcha challenge (by forwarding it to the user)
    """
    print(reason)
    for __ in range(website.captcha_tries):

        captcha = request_get(website, url_path="captcha/show_captcha.php")
        with tempfile.NamedTemporaryFile(suffix=".png") as image_captcha:
            image_captcha.write(captcha.content)
            image_captcha.flush()
            utils.default_open(image_captcha.name)
            captcha_attempt = utils.user_input(
                "Can you read this for me please ? (should be 5 numbers) : ")

        post_data["captcha"] = captcha_attempt

        response = website.session.post(url, data=post_data)
        soup = get_soup(response)
        message = get_message(soup)
        if message and "confirmation code" in message:
            print("Invalid captcha !")
            continue
        else:
            return soup
    raise ValueError("Too many captcha errors.")


def get_soup(response):
    return BeautifulSoup(response.content, 'html.parser')


def check_solution(website, problem_id, solution):
    """
    Check that a solution for a given problem is correct, either
    by reading the html page if we already cleared it or by
    submitting it.
    """
    soup = get_logged_in_problem_page(website, problem_id)

    good_solution = get_already_found(soup)
    if good_solution:
        return good_solution == solution

    soup = solve_captcha(
        website,
        reason="Solution Check Captcha",
        post_data={"guess_{}".format(problem_id): solution},
        url=get_url(website, problem_id=problem_id)
    )

    return check_solution_answer(soup)


def get_logged_in_problem_page(website, problem_id):
    response = request_get(website, problem_id)
    soup = get_soup(response)

    info_panel = soup.select_one("#info_panel > div")
    if not info_panel or "Logged in as" not in info_panel.get_text():
        connect(website)
        response = request_get(website, problem_id)
        soup = get_soup(response)

    return soup


def check_solution_answer(soup):
    text = soup.select_one("#content").get_text()

    if "appears to be incorrect" in text:
        return False
    elif "is correct" in text:
        return True

    raise ValueError("Cannot say whether it is a success or a failure.")


def get_already_found(soup):
    already_found = soup.find(string="Answer:")

    if already_found:
        if already_found.find_parent("tr").find("input"):
            return None

        good_solution = already_found.find_parent("tr").find("b").string
        return int(good_solution)

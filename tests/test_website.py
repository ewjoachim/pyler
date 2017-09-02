import os
import pathlib
import tempfile

import pytest

from pyler import website as w
from pyler.config import Config


class FakeResponse(object):
    def __init__(self, content, url, code=200):
        self.content = content
        self.url = url
        self.code = code


SAVED = pathlib.Path(__file__).parent / "saved_html"


class FakeSession(object):
    cookies = b"yay"

    def __init__(self):
        self.posted_data = []
        self.answers = []
        self.history = []

    def get(self, url):
        self.history.append(url)
        try:
            path = os.path.join(SAVED, self.answers.pop(0))
        except IndexError:
            raise IndexError("Not enough pages prepared (history: {})".format(
                ", ".join(self.history)))
        with open(path, "rb") as f:
            return FakeResponse(
                content=f.read(),
                url=url)

    def post(self, url, data):
        self.posted_data.append(data)
        return self.get(url)


class FakeWebsite(w.Website):
    base_url = ""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._session = FakeSession()

    def add_answers(self, *answers):
        self.session.answers.extend(answers)

    @property
    def session(self):
        return self._session


@pytest.fixture
def website():
    website = FakeWebsite()
    website.base_url = ""

    return website


@pytest.fixture
def config():
    config = Config()
    with tempfile.NamedTemporaryFile() as f:
        os.environ["PYLER_CONF"] = f.name
        yield config


@pytest.fixture
def input(mocker):
    input = mocker.patch("pyler.utils.user_input")
    return input


@pytest.fixture
def default_open(mocker):
    input = mocker.patch("pyler.utils.default_open")
    return input


def test_get_problem_content(website):
    """
    Looking at the file solved_problem.html, we successfully extract
    the problem content.
    """
    website.add_answers("solved_problem.html")
    content = w.get_problem_content(website, problem_id=1)
    assert content.startswith("If we list all the natural numbers")


def test_connect(config, website, input, default_open):
    """
    We try to connect to the project euler website, and answer the catcha
    challenge. All goes well.
    """
    input.side_effect = ["yay", "hoy", "12345"]

    website.add_answers("captcha.png", "sign_in_successful.html")
    w.connect(website)

    assert config["credentials"] == {"username": "yay", "password": "hoy"}
    assert config["session"] == "eWF5"  # yay in base64
    assert website.session.posted_data == [{'captcha': '12345',
                                            'username': 'yay',
                                            'password': 'hoy',
                                            'remember_me': '1',
                                            'sign_in': 'Sign In'}]


def test_connect_no_credentials(input, website, config):
    """
    We fail to answer at the login prompt. Test that we get
    the correct exception
    """
    input.side_effect = ["haha", ""]

    with pytest.raises(ValueError) as exc:
        w.connect(website)

    assert str(exc.value) == "Cannot connect without credentials"


def test_connect_wrong_credentials(input, website, config, default_open):
    """
    Bad credentials result in the correct exception.
    """
    input.side_effect = ["haha", "huhu", "12345"]

    website.add_answers("captcha.png", "sign_in_wrong_password.html")

    with pytest.raises(ValueError) as exc:
        w.connect(website)

    assert str(exc.value) == "Unsuccessful login :("


def test_load_session_cookies(mocker):
    """
    Cookies as read from base64
    """
    config = {"session": "eWF5"}
    session = mocker.Mock()

    w.load_session_cookies(config, session)
    assert session.cookies == b"yay"


def test_save_session_cookies(mocker):
    """
    Cookies are stored as base64
    """
    config = {}
    session = mocker.Mock(cookies=b"yay")

    w.save_session_cookies(config, session)

    assert config["session"] == "eWF5"


def test_get_url(website):
    """
    The get_url function can give us the url of a problem, as
    well as any other url from the website.
    """
    website.base_url = "http://abc.def"

    assert(w.get_url(website, 1) == "http://abc.def/problem=1")
    assert(w.get_url(website, problem_id=1) == "http://abc.def/problem=1")
    assert(w.get_url(website, url_path="bla") == "http://abc.def/bla")


def test_solve_captcha_login(website, input, default_open):
    """
    When logging in, we have a captcha. Test that we open it right.
    """
    input.side_effect = ["12345"]

    website.add_answers("captcha.png", "sign_in_successful.html")
    w.solve_captcha(website, "test", {}, "")

    assert website.session.posted_data == [{'captcha': '12345'}]


def test_solve_captcha_login_errors(website, input, default_open):
    input.side_effect = ["12345", "54321", "13243"]

    website.add_answers(*(["captcha.png", "sign_in_wrong_captcha.html"] * 3))

    with pytest.raises(ValueError) as exc:
        w.solve_captcha(website, "test", {}, "")

    assert str(exc.value) == "Too many captcha errors."


def test_solve_captcha_problem(website, input, default_open):
    input.side_effect = ["12345", "54321", "13243"]

    website.add_answers("captcha.png", "answer_incorrect_captcha.html",
                        "captcha.png", "answer_incorrect_captcha.html",
                        "captcha.png", "answer_correct.html",)

    result = w.solve_captcha(website, "test", {}, "bla")

    assert website.session.history == [
        "captcha/show_captcha.php", "bla"] * 3

    assert "Congratulations" in result.select_one("#content").get_text()


def test_get_soup(mocker):
    with open(SAVED / "solved_problem.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    assert "If we list all the natural numbers" in (
        soup.select_one(".problem_content").get_text())


def test_check_solution_answer_good(mocker):
    with open(SAVED / "answer_correct.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    assert w.check_solution_answer(soup)


def test_check_solution_answer_bad(mocker):
    with open(SAVED / "answer_incorrect.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    assert not w.check_solution_answer(soup)


def test_check_solution_answer_no_answer(mocker):
    with open(SAVED / "solved_problem.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    with pytest.raises(ValueError) as exc:
        w.check_solution_answer(soup)

    assert "Cannot say whether" in str(exc.value)


def test_get_already_found_yes(mocker):
    with open(SAVED / "solved_problem.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    assert w.get_already_found(soup) == 233168


def test_get_already_found_no(mocker):
    with open(SAVED / "new_problem.html") as f:
        soup = w.get_soup(mocker.Mock(content=f.read()))

    assert w.get_already_found(soup) is None


def test_get_logged_in_problem_page_logged_in(website):
    website.add_answers("new_problem.html")

    w.get_logged_in_problem_page(website, 1)

    assert website.session.history == ["problem=1"]


def test_get_logged_in_problem_page_not_logged_in(website, config, input, default_open):
    input.side_effect = ["yay", "hoy", "12345"]
    website.add_answers("anonymous_problem.html",
                        "captcha.png", "sign_in_successful.html",
                        "new_problem.html")

    w.get_logged_in_problem_page(website, 1)

    assert website.session.history == [
        "problem=1", "captcha/show_captcha.php", "sign_in", "problem=1"]


def test_check_solution_solved_correct(website):

    website.add_answers("solved_problem.html")

    assert w.check_solution(website, 1, 233168) is True


def test_check_solution_solved_incorrect(website):

    website.add_answers("solved_problem.html")

    assert w.check_solution(website, 1, 233135) is False


def test_check_solution_new_correct(website, input, default_open):
    input.side_effect = ["12321"]

    website.add_answers("new_problem.html", "captcha.png",
                        "answer_correct.html")

    assert w.check_solution(website, 1, 233168) is True


def test_check_solution_new_incorrect(website, input, default_open):
    input.side_effect = ["12321"]

    website.add_answers("new_problem.html", "captcha.png",
                        "answer_incorrect.html")

    assert w.check_solution(website, 1, 233135) is False

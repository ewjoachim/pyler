import signal
import unittest
import time

from . import website as w


class EulerProblem(unittest.TestCase):

    problem_id = None

    def solver(self, input_val):
        raise NotImplementedError()

    simple_input = None
    simple_output = None
    real_input = None

    def solve_real(self):
        """
        Returns the solution of the Problem for the real input
        """
        return self.solver(self.real_input)

    def solve_simple(self):
        """
        Returns the solution of the Problem for the simple input
        """
        return self.solver(self.simple_input)

    @classmethod
    def setUpClass(cls):
        if cls.solver is EulerProblem.solver:
            raise unittest.SkipTest(
                "Not running the tests for a not implemented problem")

    def test_simple(self):
        """
        Checks the simple example
        """
        self.assertEqual(self.solve_simple(), self.simple_output)

    def test_real(self):
        """
        Checks the real problem against the website
        """
        website = w.Website()
        real_output = self.solve_real()
        self.assertTrue(w.check_solution(
            website, self.problem_id, solution=real_output))

    # Windows has no Alarm signal. Sorry pal.
    use_signal = hasattr(signal, "SIGALRM")

    def test_time(self):
        """
        Checks that the real problem runs under a minute
        """
        time_limit = 60

        try:
            if self.use_signal:
                def handler(signum, frame):  # pylint: disable=unused-argument
                    raise TimeoutError()
                old_handler = signal.signal(signal.SIGALRM, handler)
                signal.alarm(time_limit)
            before = time.time()
            self.solve_real()
            after = time.time()
            if after - before > time_limit:
                raise TimeoutError()
        except TimeoutError:
            self.fail("Test failed to end in less than a minute.")
        finally:
            if self.use_signal:
                signal.signal(signal.SIGALRM, old_handler)

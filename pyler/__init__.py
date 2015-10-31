import signal
import unittest
import time

from .website import Website


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
            raise unittest.SkipTest("Not running the tests for a not implemented problem")

    def test_1_simple_solution_correct(self):
        self.assertEqual(self.solve_simple(), self.simple_output)

    def test_2_real_solution_correct(self):
        website = Website()
        real_output = self.solve_real()
        self.assertTrue(website.check_solution(self.problem_id, solution=real_output))

    # Windows has no Alarm signal. Sorry pal.
    use_signal = hasattr(signal, "SIGALRM")

    def test_3_runs_under_one_minute(self):
        time_limit = 60

        try:
            if self.use_signal:
                def handler(signum, frame):
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
            signal.signal(signal.SIGALRM, old_handler)

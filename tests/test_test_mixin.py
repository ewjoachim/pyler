import unittest
from pyler import EulerProblem


class Problem1(EulerProblem):
    """
    Multiples of 3 and 5
    ====================
    Problem 1
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.
    """
    problem_id = 1
    simple_input = 10
    simple_output = 23
    real_input = 1000

    def solver(self, input_val):
        return sum(element for element in range(input_val) if any(element % x == 0 for x in [3, 5]))


class BadProblem1(EulerProblem):
    """
    Multiples of 3 and 5
    ====================
    Problem 1
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we get 3, 5, 6 and 9. The sum of these multiples is 23.

    Find the sum of all the multiples of 3 or 5 below 1000.
    """
    problem_id = 1

    def solver(self, input_val):
        return 14

    def test_simple(self):
        with self.assertRaises(AssertionError):
            super().test_simple()

    def test_real(self):
        with self.assertRaises(AssertionError):
            super().test_real()

    simple_input = 10
    simple_output = 23
    real_input = 1000

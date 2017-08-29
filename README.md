[![PyPI version](https://badge.fury.io/py/pyler.svg)](https://badge.fury.io/py/pyler)

Pyler
=====

Pyler is a lib that helps tackling Project Euler problems using Python

How ?
=====

```bash
pip install pyler
```

Generate a file
---------------

```bash
# generates the file for problem 1
pyler gen 1
# generates the file for problems 1 to 10, 14 and 17 to 24
pyler gen 1-10,14,17-24
# generates the first not-yet-generated problem
pyler gen next
# generates all available problems
pyler gen all
```

You get the idea !

This will generate a file that has more or less everything for beginning the real work.
Just fill the variables and code your solution into solver.

```python
from pyler import EulerProblem


class Problem0001(EulerProblem):
    """
    If we list all the natural numbers below 10 that are multiples of 3 or 5, we
    get 3, 5, 6 and 9. The sum of these multiples is 23. Find the sum of all the
    multiples of 3 or 5 below 1000.
    """
    problem_id = 1
    simple_input = 0
    simple_output = 1
    real_input = 0

    def solver(self, input_val):
        return 0

if __name__ == '__main__':
    import unittest
    unittest.main()

```

You can change the path where the files are being generated using ``--path`` and
the template used with ``--template=path/to/template.py``, the template file must be compatible
with Python's [``.format``](https://pyformat.info/) function and will recieve 2 variables : ``doc``
and ``problem_id``

BTW : yes, the docstring is scraped from the website.

Test your solution
------------------

```bash
# Tests the implementation of the first problem
pyler test 1
# Well I'm sure you know what this does
pyler test 1-10,14,17-24
# Tests the last problem
pyler test last
```

You may also use unittest or the testing tool of your choice that accept unittest TestCases.
Calling Python on the problem file directly will also launch the tests.

Launching the tests on your solution module will test your solution for :

 * The simple test case
 * The real test case (it will check on the real website to do so
   * the first time, it will ask for your credentials (stored in a local
     file ``pyler.conf``) and now and then, it will ask you to solve the
     captchas.
     If you have already validated the problem, it will check the solution
     from the page. Otherwise, it will submit the solution for you.
 * A test ensuring that your implementation takes less than 1 minute. If
   you're not using Windows, it will stop at 1 minute. Otherwise, it will
   fail when the computation is over.

You can use any number of ``--only=x`` and ``--skip=x`` flags with x
being ``simple``, ``real``, ``time``.

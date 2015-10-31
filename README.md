Pyler
=====

Pyler is a lib that helps tackling Project Euler problems using Python

How ?
=====

```bash
pip install pyler
```
(TODO : it's not on pypi yet ^^)

Generate a file
---------------

```bash
pyler gen . 1
```

This will generate a file that has more or less everything for beginning the real work.
Just fill the variables.

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
        return 1

```

BTW : yes, the docstring is scraped from the website.

Test your solution
------------------

```bash
pyler test 1
```
(TODO : Not working yel but you can do ``python -m unittest problem_0001``)

Launching unittest on your solution module will test your solution for :

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

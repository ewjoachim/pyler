import sys
import os
import unittest
import textwrap

from .website import Website

TEMPLATE = """from pyler import EulerProblem


class Problem{problem_id:04d}(EulerProblem):
    \"""
    {doc}
    \"""
    problem_id = {problem_id}
    simple_input = 0
    simple_output = 1
    real_input = 0

    def solver(self, input_val):
        return 1
"""


def usage():
    print("Usage : pyler gen path {problem_id}")
    print("     or pyler test {problem_id}")
    sys.exit(1)


def main():
    try:
        command, = sys.argv[1:2]
        args = sys.argv[2:]
    except (ValueError, TypeError):
        usage()
    if command == "gen":
        path, problem_id = args
        problem_id = int(problem_id)
        doc = Website().get_problem_content(problem_id)
        doc = textwrap.fill(doc, 76).replace("\n", "\n    ")
        with open(os.path.join(path, "problem_{:04d}.py".format(problem_id)), "w") as handler:
            handler.write(TEMPLATE.format(
                problem_id=problem_id,
                doc=doc,
            ))
    elif command == "test":
        raise NotImplementedError()
        # Todo.
        # It's probably as simple as a unittest.main() with the right arguments.
    else:
        usage()

if __name__ == '__main__':
    main()

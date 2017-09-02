import os
import glob
import unittest
import textwrap
import argparse
import re
import sys
import itertools

from . import website as w

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
        raise NotImplementedError


if __name__ == '__main__':
    import unittest
    unittest.main()

"""

FILE_NAME_TEMPLATE = "problem_{:04d}.py"
FILE_NAME_REGEX = r"problem_(\d{4})\.py"
FILE_NAME_GLOB = "problem_*.py"


def iter_problem_ids(problem_string):
    if problem_string in ("all", "next", "last"):
        return problem_string

    ids = set()
    for group in problem_string.split(","):
        group = group.strip()
        if not group:
            continue
        group = group.split("-")
        if len(group) > 2:
            raise argparse.ArgumentTypeError(
                "Incorrect format for problem_id (range with more "
                "than 2 borders)")
        try:
            group = [int(one_id) for one_id in group]
        except ValueError:
            raise argparse.ArgumentTypeError(
                "Incorrect format for problem_id (not an integer)")

        if len(group) == 2:
            ids |= set(range(*sorted(group)))
        else:
            ids.add(group[0])

    if any(element < 1 for element in ids):
        raise argparse.ArgumentTypeError(
            "Incorrect format for problem_id (null or negative "
            "integer)")

    return sorted(ids)


def complete_problem_ids(problem_ids, path):
    if problem_ids == "all":
        return None
    elif problem_ids in ["next", "last"]:
        last_problem = max(all_files(path))
        last_id = int(re.match(FILE_NAME_REGEX, last_problem).groups()[0])
        if problem_ids == "next":
            return [last_id + 1]
        return [last_id]
    return problem_ids


def all_files(path):
    try:
        current = os.getcwd()
        os.chdir(path)
        return glob.glob(FILE_NAME_GLOB)
    finally:
        os.chdir(current)


def gen_files(problem_ids, path, force=False, template=None):
    problem_ids = complete_problem_ids(problem_ids, path)
    if problem_ids is None:
        problem_ids = itertools.count(1)

    website = w.Website()
    for problem_id in problem_ids:

        if template:
            with open(template, "r") as template_handler:
                template_str = template_handler.read()
        else:
            template_str = TEMPLATE

        problem_id = int(problem_id)
        try:
            doc = w.get_problem_content(website, problem_id)
        except ValueError:
            break
        doc = textwrap.fill(doc, 76).replace("\n", "\n    ")

        file_path = os.path.join(path, FILE_NAME_TEMPLATE.format(problem_id))

        if not force and os.path.exists(file_path):
            print("skipping {}".format(problem_id))
            continue

        file_name = FILE_NAME_TEMPLATE.format(problem_id)
        with open(os.path.join(path, file_name), "w") as handler:
            handler.write(template_str.format(
                problem_id=problem_id,
                doc=doc,
            ))


def test_files(problem_ids, path, only, skip):
    problem_ids = complete_problem_ids(problem_ids, path)

    only = only or ["real", "simple", "time"]
    tests = {"test_{}".format(test_name)
             for test_name in set(only) - set(skip)}

    sys.path.insert(0, os.path.abspath(path))

    py_files = set(all_files(path))

    if problem_ids is not None:
        wanted_files = {FILE_NAME_TEMPLATE.format(problem_id)
                        for problem_id in problem_ids}
        py_files = py_files & wanted_files

    modules = [
        "{}.Problem{}".format(file_name[:-3], file_name[-7:-3])
        for file_name in py_files]

    tests_names = sorted(
        ".".join(module_test)
        for module_test in itertools.product(modules, tests))

    unittest.main(module=None, argv=[""] + tests_names)


def main():
    # create the top-level parser
    parser = argparse.ArgumentParser(prog='pyler')
    parser.add_argument('--path', '-p', '--to',
                        default=".",
                        help="The folder in which problem files will be found")

    problem_ids_kwargs = {
        "type": iter_problem_ids,
        "help": "The id(s) to generate or 'all', 'last', "
                "'next'. Ex: '1', '1,2', '1-12,37-60' "
    }

    subparsers = parser.add_subparsers()

    parser_gen = subparsers.add_parser(
        'gen',
        help="Generate a testcase file for a given problem")
    parser_gen.add_argument(
        '--force', '-f', action='store_true',
        help="Replaces an existing file if encountered")
    parser_gen.add_argument(
        '--template', '-t',
        help="Uses a specific template file (must contain {doc} and "
             "{problem_id}).")
    parser_gen.add_argument(
        'problem_ids', **problem_ids_kwargs)
    parser_gen.set_defaults(callback=gen_files)

    parser_test = subparsers.add_parser('test', help="Tests")

    tests = ["simple", "real", "time"]
    parser_test.add_argument('problem_ids', **problem_ids_kwargs)
    parser_test.add_argument(
        '--skip', action="append", default=[],
        help="Skip some tests among {}. (you can have several of these)"
             "".format(", ".join(tests))
    )
    parser_test.add_argument(
        '--only', action="append", default=[],
        help="Only run tests among {}. (you can have several of these)"
             "".format(", ".join(tests))
    )
    parser_test.set_defaults(callback=test_files)

    args = vars(parser.parse_args())
    args.pop("callback")(**args)


if __name__ == '__main__':
    main()

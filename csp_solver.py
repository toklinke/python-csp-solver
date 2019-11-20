#!/usr/bin/env python3
# MIT License
#
# Copyright (c) 2019 Tobias Klinke
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Load a CSP module and try to solve it using domain splitting and
arc consistency algorithm.
"""
import argparse
import itertools
from pathlib import Path
from pprint import pprint
from typing import Any, Dict, Iterable, Set, Tuple

from csp import CSP, RepresentationFunc
from arc_consistency import arc_consistency
from domain_splitting import domain_splitting

def parse_args() -> argparse.Namespace:
    """
    Parse command line arguments.

    Returned namespace attributes:

    csp_module: str - The CSP module path.
    find_all: bool - Find all solutions or just one.
    """
    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument("csp_module",
                        help="Python module describing the CSP to be solved")

    parser.add_argument("--find-all", "-a", action="store_true",
                        help="Find all solutions")

    args = parser.parse_args()
    return args

def print_solution(solution: Dict[str, Any],
                   representation: RepresentationFunc) -> None:
    """ Print solution """
    print("Solution:")
    if representation:
        print(representation(solution))
    else:
        pprint(solution)
    print("")

def find_one_solution(csp: CSP) -> None:
    """ Find and print one solution """
    solutions = domain_splitting(csp)
    has_solution = False
    for solution in solutions:
        has_solution = True
        print_solution(solution, csp.representation)
        break
    if not has_solution:
        print("No solution.")


def find_all_solutions(csp: CSP) -> None:
    """ Find and print all solutions """
    solutions = list(domain_splitting(csp))
    for solution in solutions:
        print_solution(solution, csp.representation)


def main():
    """ Main program """
    args = parse_args()

    csp = CSP.from_file(Path(args.csp_module))

    if args.find_all:
        find_all_solutions(csp)
    else:
        find_one_solution(csp)

if __name__ == "__main__":
    main()

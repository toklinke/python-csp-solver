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

""" Domain splitting algorithm for solving CSPs. """
import itertools
from typing import Any, Dict, Iterable, Set, Tuple

from csp import CSP
from arc_consistency import arc_consistency

def domain_splitting(csp: CSP, debug: bool=True) -> Iterable[Dict[str, Any]]:
    """
    Solve a CSP using domain splitting and arc consistency.

    Generate assignment of all variables with exactly one value,
    if CSP has a solution.
    If the CSP has no solution, the returned iterator is empty.
    """
    domains = arc_consistency(csp)

    if some_empty(domains):
        pass # no solution
    elif unique(domains):
        yield {var: list(domain)[0]
               for var, domain in domains.items()}
    else:
        split_var = get_split_var(domains)
        partition = partition_domain(domains[split_var])
        new_csps = [make_split_csp(csp, domains, split_var, split_domain)
                    for split_domain in partition]

        if debug:
            print("Split '{var}' in '{d1}' and '{d2}'"
                  .format(var=split_var, d1=partition[0], d2=partition[1]))

        # TODO: Customize agenda so that not everything needs to be rechecked
        for solution in domain_splitting(new_csps[0]):
            yield solution
        for solution in domain_splitting(new_csps[1]):
            yield solution


def some_empty(domains: Dict[str, Set[Any]]) -> bool:
    """ The domain for at least one variable is empty. """
    return any((not domain for domain in domains.values()))

def unique(domains: Dict[str, Set[Any]]) -> bool:
    """ Each variable has exactly one value """
    return all((len(domain) == 1
                for domain in domains.values()))

def get_split_var(domains: Dict[str, Set[Any]]) -> str:
    """
    Get a variable that can be used for splitting (has more
    than one possible value).
    """
    # Just select the first one that is found
    # TODO: One could implement better selection strategies.
    for var, domain in domains.items():
        if len(domain) > 1:
            return var
    # Not reachable because otherwise the solution
    # is unique and needs no splitting
    assert False

def partition_domain(domain: Set[Any]) -> Tuple[Set[Any], Set[Any]]:
    """
    Partition a domain into two parts and return the two parts
    """
    part1 = set()
    part2 = set()

    # Add each value to either part1 or part2
    for value, new_part in zip(domain, itertools.cycle([part1, part2])):
        new_part.add(value)

    return part1, part2


def make_split_csp(csp: CSP, new_domains: Dict[str, Set[Any]],
                   split_var: str, split_domain: Set[Any]) -> CSP:
    """ Make a new CSP with split_var's domain replaced by new_domain """
    domains = new_domains.copy()
    domains.update({split_var: split_domain})
    return CSP(variables=domains,
               constraints=csp.constraints,
               representation=csp.representation)


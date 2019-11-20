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

""" Implementation of arc consistency algorithm """
from collections import namedtuple
import copy
from typing import Any, Dict, Iterable, List, Set

from csp import CSP

# An arc in a constraint network
Arc = namedtuple("Arc", ["constraint", "variable"])

class Agenda:
    """ An agenda for arc consistency algorithm """
    def __init__(self) -> None:
        self._arcs = set()

    def add_arc(self, arc: Arc) -> None:
        """ Add new arc """
        self._arcs.add(arc)

    def next_arc(self) -> Arc:
        """
        Remove and return next arc according to selection strategy
        """
        return self._arcs.pop()

    @property
    def is_empty(self) -> bool:
        """ True, if frontier is empty (no more arcs left) """
        return not self._arcs

    def __len__(self) -> int:
        return len(self._arcs)


debug = True
def debug_print(x: Any):
    if debug:
        print(x)

def arc_consistency(csp: CSP) -> Dict[str, Set[Any]]:
    """ Try to solve CSP by arc consistency algorithm """
    # The possible values for each variable
    domains = get_initial_domains(csp)
    # The constraint network
    arcs = list(get_initial_arcs(csp))

    # initialize agenda
    agenda = Agenda()
    for initial_arc in arcs:
        agenda.add_arc(initial_arc)

    while not agenda.is_empty:
        current_arc = agenda.next_arc()

        debug_print(current_arc)
        debug_print("{} arcs left".format(len(agenda)))

        new_domain = make_consistent(current_arc, domains)
        old_domain = domains[current_arc.variable]

        if new_domain != old_domain:
            debug_print("new_domain for {0}: {1}"
                        .format(current_arc.variable, new_domain))
            for invalid_arc in invalidated_arcs(current_arc, arcs):
                agenda.add_arc(invalid_arc)
            domains[current_arc.variable] = new_domain

    return domains

def get_initial_domains(csp: CSP) -> Dict[str, Set[Any]]:
    """ Get initial domains for all variables """
    # deep copy because specification of CSP could have reused domains
    # and we are going to modify the domains
    return copy.deepcopy(csp.variables)

def get_initial_arcs(csp: CSP) -> Iterable[Arc]:
    """ One arc from each constraint to all of its variables """
    for constraint in csp.constraints:
        for var in constraint.variables:
            yield Arc(constraint=constraint,
                      variable=var)

def make_consistent(arc: Arc, domains: Dict[str, Set[Any]]) -> Set[Any]:
    """
    Make an arc consistent.
    Return new domain for `arc.variable`.
    """
    other_vars = [var for var in arc.constraint.variables
                  if var != arc.variable]

    current_domain = domains[arc.variable]
    other_domains = {var: dom for (var, dom) in domains.items()
                     if var in other_vars}

    new_domain = set()
    for value in current_domain:
        for other_values in domain_product(other_domains):
            all_values = other_values
            all_values[arc.variable] = value

            if arc.constraint.check(all_values):
                new_domain.add(value)
                break

    return new_domain

Assignment = Dict[str, Any]

def domain_product(domains: Dict[str, Set[Any]]) -> Iterable[Assignment]:
    """
    Generate all possible combinations of values in domains.
    Yield an assignmnent (variable: value) from cartesian product of all
    domains.
    """
    def get_assignment(domains: Dict[str, Set[Any]]) -> Iterable[Assignment]:
        # termination
        if not domains:
            yield {}
        else:
            # Reduce by one variable and get all assingnment for remaining
            # variables
            remaining_domains = domains.copy()
            var, domain = remaining_domains.popitem()
            for remaining_assignment in get_assignment(remaining_domains):
                for value in domain:
                    remaining_assignment[var] = value
                    yield remaining_assignment
    return get_assignment(domains)

def invalidated_arcs(current_arc: Arc, arcs: List[Arc]) -> Iterable[Arc]:
    """
    Generate all arcs that have been invalidated by making
    `current_arc` consistent.
    """
    current_var = current_arc.variable

    return [arc for arc in arcs
            if arc.constraint != current_arc.constraint
            and current_var in arc.constraint.variables
            and arc.variable != current_var]


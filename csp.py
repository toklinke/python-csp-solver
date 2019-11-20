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
Module for representation of Constraint Satisfaction Problems (CSPs).
This module suspports a format of specifiying CSPs as Python modules.

You define a Python module with at least the following Variables:

- Variables: Dict[str, Set[Any]]
  Contains one key for each variable and assigns a domain of possible
  values to it.
  The key is the variable name. The value is its domain.
- Constraints: List[Callable]
  A list of constraints that must be satified for a solution of the CSP.
  Each function takes a number of arguments and returns a `bool`.
  The constraint function returns `True`, if the constraint is satifsfied.
  Otherwise, it returns `False`.
  The argument names must match the names of the variables defined
  in `Variables`. When the constraint is evaluated the values of the
  variables are bound to the arguments with the same name.

In every other aspect, the module describing the CSP is imported as
a normal Python module. So the full power of Python can be used.


Example module:

    Variables = {"A": {1, 2, 3, 4},
                 "B": {1, 2, 3},
                 "C": {0, 1}
                }

    def ConstraintLessThanAB(A, B):
        return A < B

    def ConstraintAllDifferent(A, B, C):
        return (A != B) and (A != C) and (B != C)

    def ConstraintDifference(A, B, C):
        return C == B - A

    Constraints = [ConstraintLessThan,
                   ConstraintAllDifferent,
                   ConstraintDifference
                  ]

This CSP has two solutions:
A = 1, B = 2, C = 1
A = 2, B = 3, C = 1
"""
import importlib
import inspect
from pathlib import Path
import sys
from typing import Any, Callable, Dict, List, Optional, Set

class Constraint:
    """ A constraint in a CSP """
    def __init__(self, function: Callable, *,
                 variables: Optional[List[str]] = None,
                 name: Optional[str] = None) -> None:
        self.function = function
        self._variables = variables
        self._name = name

    @property
    def variables(self) -> List[str]:
        """ Names of all variables that are involved in this constraint """
        if self._variables is not None:
            return self._variables
        signature = inspect.signature(self.function)
        func_params = list(signature.parameters.keys())
        return func_params

    @property
    def name(self) -> str:
        """ Name of the constraint """
        if self._name is not None:
            return self._name
        return self.function.__name__

    def check(self, assignment: Dict[str, Any]) -> bool:
        """ Evaluate constraint for an assignment of variables """
        return self.function(**assignment)

    def __str__(self) -> str:
        result = "{}({})".format(self.name, ", ".join(self.variables))
        return result

    def __repr__(self) -> str:
        return str(self)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Constraint):
            return self.function == other.function
        return False

    def __hash__(self) -> int:
        return hash(self.function)


RepresentationFunc = Callable[[Dict[str, Any]], str]

class CSP:
    """ A Constraint Satisfaction problem """
    def __init__(self, variables: Dict[str, Set[Any]],
                 constraints: List[Constraint],
                 representation: Optional[RepresentationFunc]) -> None:
        self.variables = variables
        self.constraints = constraints
        self.representation = representation

    @staticmethod
    def from_module(module: Any) -> "CSP":
        """
        Construct a CSP instance from a python module
        The module must have `Variables` and `Constraints` attributes.

        Raises RuntimeError, if the module has not all required attributes.
        """
        if not hasattr(module, "Variables"):
            raise RuntimeError("Module '{0}' has no 'Variables' member."
                               .format(module.__file__))

        if not hasattr(module, "Constraints"):
            raise RuntimeError("Module '{0}' has no 'Constraints' member."
                               .format(module.__file__))

        if hasattr(module, "Representation"):
            representation = module.Representation
        else:
            representation = None

        constraints = [
            func if isinstance(func, Constraint) else Constraint(func)
            for func in module.Constraints
        ]
        return CSP(variables=module.Variables,
                   constraints=constraints,
                   representation=representation)

    @staticmethod
    def from_file(module_path: Path) -> "CSP":
        """
        Load a python module and pass it to `from_module`.

        Raise RuntimeError, if `module_path` is not a python source file.
        Raise any exception that the module raises during import.
        """
        full_path = module_path.expanduser().resolve()

        if full_path.suffix != ".py":
            raise RuntimeError("'{0}' is not a python module."
                               .format(str(full_path)))

        # Add to path to be able to import the module by name
        # Also any imports from the imported module can be resolved correctly.
        # The path is inserted in the beginning to make it take precedency over
        # any other modules in sys.path with the same name.
        directory = full_path.parent
        sys.path.insert(0, str(directory))

        module_name = full_path.stem
        module = importlib.import_module(module_name)
        return CSP.from_module(module)

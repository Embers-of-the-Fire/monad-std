# About this module
#
# This file is part of the `typeshed` package included in the cpython standard library.
#
# Since std libraries are not implemented in python, only `pyi` files are provided to use.
# However, this library is implemented with pure Python, and there's no need to write single
# type definitions, which means we cannot use the `typeshed` package.
#
# For internal use and for static type checking, part of the `typeshed` package is copied
# and partly changed. It is guaranteed that the `monad-std` package will not use any of the
# code except for type hints.

from . import cmp
from . import ops

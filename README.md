# Monad STD

<div style="text-align: center;">

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/Embers-of-the-Fire/monad-std/test-python-package.yml?branch=main&logo=github)](https://github.com/Embers-of-the-Fire/monad-std/actions)
![python version](https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python)
[![Codecov](https://img.shields.io/codecov/c/github/Embers-of-the-Fire/monad-std?logo=codecov)](https://app.codecov.io/gh/Embers-of-the-Fire/monad-std)
[![PyPI - Downloads](https://img.shields.io/pypi/dm/monad-std?logo=pypi)](https://pypi.org/project/monad-std/)

</div>

`monad_std` is a library that provides some useful Rust-styled utilities for using monads in Python.

<div style="text-align: center;">

[Documentation](https://embers-of-the-fire.github.io/monad-std/) | [PyPI Page](https://pypi.org/project/monad-std/)

</div>

## Quick Start

To install this library, simply use your favorite package manager, here we use pure pip.

```bash
pip install monad-std
```

Then, import the library:

```python-repl
>>> from monad_std import *
>>> Result.of_ok(2)
Result::Ok(2)
```

Now you could use the utilities this library provides. For more information and examples, see the documentation above.

## Contribution

Any issue and pull request is welcomed, and you can directly make a pr for new features or open an issue for bug reports.

## Future Plan

Until now, this library provides the following features:

- `monad_std.Option`: An optional value.
- `monad_std.Result`: A structure containing a success value or an error.

And the following are being developed:

- `monad_std.Either`: A structure containing two type of values, but not that specific like `monad_std.Result`
- A better entry point for those utilities.

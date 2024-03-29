<div style="text-align: center; display: flex; flex-direction: row; justify-content: center; align-items: center;">
<img alt="Logo" height="150" src="logo.svg" width="150"/>
</div>

# Monad STD

<div style="text-align: center;">

[![GitHub Workflow Status (with event)](https://img.shields.io/github/actions/workflow/status/Embers-of-the-Fire/monad-std/test-python-package.yml?branch=main&logo=github)](https://github.com/Embers-of-the-Fire/monad-std/actions)
![python version](https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python)
[![codecov](https://codecov.io/gh/Embers-of-the-Fire/monad-std/graph/badge.svg?token=FIXN2JM4QG)](https://codecov.io/gh/Embers-of-the-Fire/monad-std)
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
>>> Ok(2)
Result::Ok(2)
```

Now you could use the utilities this library provides. For more information and examples, see the documentation above.

For a better guide, see [the documentation's quick start guide](https://embers-of-the-fire.github.io/monad-std/quick%20start/).

## Contribution

Any issue and pull request is welcomed, and you can directly make a pr for new features or open an issue for bug reports.

## Future Plan

Until now, this library provides the following features:

- `monad_std.Option`: An optional value.
- `monad_std.Result`: A structure containing a success value or an error.
    - `monad_std.Ok`: A successful value.
    - `monad_std.Err`: An error value.
- `monad_std.std_types`: Wrapped api around std types.
- `monad_std.iter`: Iterator interface with functors and monads support.
- `monad_std.Either`:
  A structure containing two type of values, but not that specific like `monad_std.Result`.
  (Currently under development.)

# Monad STD

<div style="text-align: center;">

<a href="https://github.com/Embers-of-the-Fire/monad-std/actions"><img alt="GitHub Workflow Status (with event)" src="https://img.shields.io/github/actions/workflow/status/Embers-of-the-Fire/monad-std/test-python-package.yml?branch=main&logo=github" /></a>
<img alt="python version" src="https://img.shields.io/badge/python-%E2%89%A53.8-blue?logo=python" />
<a href="https://codecov.io/gh/Embers-of-the-Fire/monad-std" >
<img src="https://codecov.io/gh/Embers-of-the-Fire/monad-std/graph/badge.svg?token=FIXN2JM4QG"/>
</a>
<a href="https://pypi.org/project/monad-std/"><img alt="PyPI - Downloads" src="https://img.shields.io/pypi/dm/monad-std?logo=pypi" /></a>

</div>

`monad_std` is a library that provides some useful Rust-styled utilities for using monads in Python.

<div style="text-align: center;">

<a href="https://embers-of-the-fire.github.io/monad-std/">Documentation</a> | <a href="https://pypi.org/project/monad-std/">PyPI Page</a>

</div>

## Quick Start

To install this library, simply use your favorite package manager, here we use pure pip.

```bash
pip install monad-std
```

Then, import the library:

```python
>>> from monad_std import *
>>> Result.of_ok(2)
Result::Ok(2)
```

Now you could use the utilities this library provides. For more information and examples, see the documentation above.

## Contribution

Any issue and pull request is welcomed, and you can directly make a pr for new features or open an issue for bug reports.

## Future Plan

Until now, this library provides the following features:

-   `monad_std.Option`: An optional value.
-   `monad_std.Result`: A structure containing a success value or an error.

And the following are being developed:

-   `monad_std.Either`: A structure containing two type of values, but not that specific like `monad_std.Result`
-   A better entry point for those utilities.

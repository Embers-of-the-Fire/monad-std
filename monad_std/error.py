import typing as t
import typing_extensions as te

ExceptionType: te.TypeAlias = t.Literal["Option", "Result", "Either"]


class UnwrapException(Exception):
    exception_type: ExceptionType
    msg: str

    def __init__(self, etype: ExceptionType, msg: str):
        super().__init__(self)
        self.exception_type = etype
        self.msg = msg

    def __str__(self):
        if self.exception_type == 'Option':
            return f'OptionError: {self.msg}'
        elif self.exception_type == 'Result':
            return f'ResultError: {self.msg}'
        elif self.exception_type == 'Either':
            return f'EitherError: {self.msg}'
        else:
            raise TypeError(f'Unknown exception type: {self.exception_type}')

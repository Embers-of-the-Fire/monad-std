import typing as t

ExceptionType = t.NewType('ExceptionType', t.Union[t.Literal['Option'], t.Literal['Result']])


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
        else:
            raise TypeError(f'Unknown exception type: {self.exception_type}')

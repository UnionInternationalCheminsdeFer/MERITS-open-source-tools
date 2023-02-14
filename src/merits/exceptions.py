"""
This project is designed to NOT use flow-by-exception. Exceptions should be exceptional and should only be handled at or
near the top of the stack.
"""


class MeritsException(Exception):
    """
    An exception that the code may raise if something unexpected goes wrong.
    """
    pass

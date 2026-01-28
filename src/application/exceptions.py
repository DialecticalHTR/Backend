class ConcurencyException(Exception):
    pass


class StaleDataException(ConcurencyException):
    pass

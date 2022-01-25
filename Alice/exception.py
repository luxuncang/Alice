class AliceException(Exception):

    def __init__(self, name: str, reason: str) -> None:
        self.name = name
        self.reason = reason

    def __str__(self) -> str:
        return f"{self.name}: {self.reason}"

class ParseException(AliceException):

    def __init__(self, name: str = 'ParseException', reason: str = 'GraiaMacth parse exception.') -> None:
        super().__init__(name , reason)

class AliceSessionStop(AliceException):

    def __init__(self, name: str = 'AliceSessionStop', reason: str = 'Session stop.') -> None:
        super().__init__(name , reason)
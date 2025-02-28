from pydantic import BaseModel

class ErrorModel(BaseModel):
    """Modelo para respostas de erros
    """
    mensagem: str
    exception: str

    @classmethod
    def from_exception(cls, exception: Exception):
        """
        Creates an instance of the class from an exception.
        Args:
            exception (Exception): The exception to create the instance from.
        Returns:
            An instance of the class with the exception message and exception type.
        """
        return cls(
            mensagem=str(exception),
            exception=exception.__class__.__name__
        )

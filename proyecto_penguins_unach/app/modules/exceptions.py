class ErrorDeDatos(Exception):
    """Clase base."""
    pass

class DataInvalidaError(ErrorDeDatos):
    """
    Excepción personalizada para cuando el dataset de pingüinos
    no cumple con la estructura o calidad mínima.
    """
    def __init__(self, mensaje="El archivo CSV no es válido para este análisis."):
        self.mensaje = mensaje
        super().__init__(self.mensaje)
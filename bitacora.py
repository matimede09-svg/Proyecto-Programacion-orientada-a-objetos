from datetime import datetime
from estados import TipoEvento


class EventoBitacora:

    def __init__(self, tipo, descripcion):
        if not isinstance(tipo, TipoEvento):
            raise ValueError("Tipo de evento inválido")
        if not descripcion:
            raise ValueError("El evento necesita una descripción")

        self.__fecha = datetime.now()
        self.__tipo = tipo
        self.__descripcion = descripcion

    def formatear(self):
        return (self.__fecha.strftime("%Y-%m-%d %H:%M:%S") + " | "
                + self.__tipo.value + " | " + self.__descripcion)


class BitacoraEventos:

    def __init__(self):
        self.__eventos = []

    def registrar(self, tipo, descripcion):
        # Composición: la bitácora crea sus propios eventos.
        self.__eventos.append(EventoBitacora(tipo, descripcion))

    def listarEventos(self):
        return [evento.formatear() for evento in self.__eventos]

    def generarReporte(self):
        return "\n".join(self.listarEventos())

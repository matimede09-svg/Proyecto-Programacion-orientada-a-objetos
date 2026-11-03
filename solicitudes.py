from estados import EstadoSolicitud
from cargas import Carga
from robots import Robot


class SolicitudEntrega:

    def __init__(self, id, origen, destino, distanciaKm, carga):
        if not id:
            raise ValueError("La solicitud necesita un ID")
        if not origen or not destino:
            raise ValueError("Origen y destino son obligatorios")
        if distanciaKm <= 0:
            raise ValueError("La distancia debe ser mayor que cero")
        if not isinstance(carga, Carga):
            raise TypeError("La solicitud necesita una carga válida")

        self.__id = id
        self.__origen = origen
        self.__destino = destino
        self.__distanciaKm = distanciaKm
        self.__estado = EstadoSolicitud.PENDIENTE
        # Composición: la carga pertenece solo a esta solicitud. Se crea al armar
        # la solicitud y desaparece con ella (nadie más guarda una referencia).
        self.__carga = carga
        # Asociación: el robot existe por su cuenta (0..1)
        self.__robotAsignado = None
        self.__motivoFallo = None

    @property
    def id(self):
        return self.__id

    @property
    def origen(self):
        return self.__origen

    @property
    def destino(self):
        return self.__destino

    @property
    def distanciaKm(self):
        return self.__distanciaKm

    @property
    def estado(self):
        return self.__estado

    @property
    def carga(self):
        return self.__carga

    @property
    def robotAsignado(self):
        return self.__robotAsignado

    @property
    def motivoFallo(self):
        return self.__motivoFallo

    def asignarRobot(self, robot):
        if not isinstance(robot, Robot):
            raise TypeError("Se necesita un robot válido")
        if self.__estado != EstadoSolicitud.PENDIENTE:
            raise ValueError("Solo se puede asignar una solicitud pendiente")
        self.__robotAsignado = robot
        self.__estado = EstadoSolicitud.ASIGNADA

    def marcarPendiente(self):
        self.__robotAsignado = None
        self.__estado = EstadoSolicitud.PENDIENTE

    def completar(self):
        if self.__estado != EstadoSolicitud.ASIGNADA:
            raise ValueError("Solo se puede completar una solicitud asignada")
        self.__estado = EstadoSolicitud.COMPLETADA

    def marcarFallida(self, motivo):
        if self.__estado != EstadoSolicitud.ASIGNADA:
            raise ValueError("Solo puede fallar una solicitud asignada")
        if not motivo:
            raise ValueError("Indique el motivo del fallo")
        self.__motivoFallo = motivo
        self.__estado = EstadoSolicitud.FALLIDA

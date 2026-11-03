from abc import ABC, abstractmethod
from estados import EstadoRobot


def _validarDistancia(distanciaKm):
    if distanciaKm <= 0:
        raise ValueError("La distancia debe ser mayor que cero")


class Robot(ABC):

    RESERVA_BATERIA_PCT = 20   # el robot nunca debe quedar por debajo de este nivel

    def __init__(self, id, bateria, ubicacion, capacidadMaxKg,
                 velocidadKmh, consumoBateriaPorKm):

        if not id:
            raise ValueError("El robot necesita un ID")
        if not 0 <= bateria <= 100:
            raise ValueError("La batería debe estar entre 0 y 100")
        if not ubicacion:
            raise ValueError("El robot necesita una ubicación")
        if capacidadMaxKg <= 0 or velocidadKmh <= 0 or consumoBateriaPorKm <= 0:
            raise ValueError("Capacidad, velocidad y consumo deben ser positivos")

        # Privados (-)
        self.__id = id
        self.__bateria = bateria
        self.__ubicacion = ubicacion
        self.__estado = EstadoRobot.DISPONIBLE
        # Protegidos (#)
        self._capacidadMaxKg = capacidadMaxKg
        self._velocidadKmh = velocidadKmh
        self._consumoBateriaPorKm = consumoBateriaPorKm

    # ---- Lectura (sin setters: nadie cambia estos datos desde fuera) ----
    @property
    def id(self):
        return self.__id

    @property
    def bateria(self):
        return self.__bateria

    @property
    def ubicacion(self):
        return self.__ubicacion

    @property
    def estado(self):
        return self.__estado

    # ---- Comportamiento ----
    def puedeTransportar(self, solicitud):
        carga = solicitud.carga

        if carga.pesoKg > self._capacidadMaxKg:
            return False
        if solicitud.destino not in self.zonasPermitidas():
            return False
        if not self.admiteCarga(carga):
            return False

        limite = carga.tiempoMaximoMin()
        if limite is not None and self.calcularTiempo(solicitud.distanciaKm) > limite:
            return False

        return True

    def tieneBateriaPara(self, distanciaKm):
        _validarDistancia(distanciaKm)
        consumo = distanciaKm * self._consumoBateriaPorKm
        return self.__bateria - consumo >= Robot.RESERVA_BATERIA_PCT

    def requiereClimaFavorable(self):
        return False

    def cambiarEstado(self, nuevoEstado):
        if not isinstance(nuevoEstado, EstadoRobot):
            raise ValueError("Estado inválido")
        if (self.__estado == EstadoRobot.EN_MANTENIMIENTO
                and nuevoEstado == EstadoRobot.EN_ENTREGA):
            raise ValueError("Un robot en mantenimiento no puede salir a entregar")
        self.__estado = nuevoEstado

    def completarViaje(self, distanciaKm, destino):
        # Actualiza batería y ubicación dentro del propio robot (encapsulamiento).
        _validarDistancia(distanciaKm)
        consumo = distanciaKm * self._consumoBateriaPorKm
        if consumo > self.__bateria:
            raise ValueError("La batería no alcanza para completar el viaje")
        self.__bateria -= consumo
        self.__ubicacion = destino

    @abstractmethod
    def calcularTiempo(self, distanciaKm):
        pass

    @abstractmethod
    def calcularCosto(self, distanciaKm, carga):
        pass

    @abstractmethod
    def zonasPermitidas(self):
        pass

    @abstractmethod
    def admiteCarga(self, carga):
        pass


class RobotRuedas(Robot):

    def calcularTiempo(self, distanciaKm):
        _validarDistancia(distanciaKm)
        return distanciaKm / self._velocidadKmh * 60

    def calcularCosto(self, distanciaKm, carga):
        _validarDistancia(distanciaKm)
        return distanciaKm * 500 + carga.recargoCosto()

    def zonasPermitidas(self):
        return ["Pasillos", "Zonas pavimentadas"]

    def admiteCarga(self, carga):
        if carga.esPeligrosa():
            return False
        if carga.esFragil():
            return carga.nivelRiesgo() <= 1
        return True


class RobotOrugas(Robot):

    def __init__(self, id, bateria, ubicacion, capacidadMaxKg,
                 velocidadKmh, consumoBateriaPorKm, factorTerreno):
        super().__init__(id, bateria, ubicacion, capacidadMaxKg,
                         velocidadKmh, consumoBateriaPorKm)
        if factorTerreno < 1:
            raise ValueError("El factor de terreno debe ser 1 o mayor")
        self.__factorTerreno = factorTerreno

    def calcularTiempo(self, distanciaKm):
        _validarDistancia(distanciaKm)
        return distanciaKm / self._velocidadKmh * 60 * self.__factorTerreno

    def calcularCosto(self, distanciaKm, carga):
        _validarDistancia(distanciaKm)
        return distanciaKm * 700 + carga.recargoCosto()

    def zonasPermitidas(self):
        return ["Pasillos", "Zonas pavimentadas", "Zonas verdes", "Terrenos irregulares"]

    def admiteCarga(self, carga):
        if carga.esPeligrosa() or carga.esFragil():
            return carga.nivelRiesgo() <= 2
        return True


class Dron(Robot): 

    def __init__(self, id, bateria, ubicacion, capacidadMaxKg,
                 velocidadKmh, consumoBateriaPorKm, alturaMaxM):
        super().__init__(id, bateria, ubicacion, capacidadMaxKg,
                         velocidadKmh, consumoBateriaPorKm)
        if alturaMaxM <= 0:
            raise ValueError("La altura máxima debe ser mayor que cero")
        self.__alturaMaxM = alturaMaxM

    @property
    def alturaMaxM(self):
        return self.__alturaMaxM

    def requiereClimaFavorable(self):
        return True

    def calcularTiempo(self, distanciaKm):
        _validarDistancia(distanciaKm)
        return distanciaKm / self._velocidadKmh * 60

    def calcularCosto(self, distanciaKm, carga):
        _validarDistancia(distanciaKm)
        return distanciaKm * 800 + carga.recargoCosto()

    def zonasPermitidas(self):
        return ["Pasillos", "Zonas abiertas"]

    def admiteCarga(self, carga):
        return not carga.esPeligrosa() and not carga.esFragil()

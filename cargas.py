from abc import ABC, abstractmethod

class Carga(ABC):

    def __init__(self, pesoKg, descripcion):
        if pesoKg <= 0:
            raise ValueError("El peso debe ser mayor que cero")
        if not descripcion:
            raise ValueError("La descripción no puede estar vacía")

        self.__pesoKg = pesoKg
        self.__descripcion = descripcion

    @property
    def pesoKg(self):
        return self.__pesoKg

    @property
    def descripcion(self):
        return self.__descripcion

    def esPeligrosa(self):
        return False

    def esFragil(self):
        return False

    def requiereTemperaturaControlada(self):
        return False

    def nivelRiesgo(self):
        # 0 = sin riesgo. Fragilidad o peligro (1 a 3) según el tipo de carga.
        # Permite que los robots decidan sin usar isinstance.
        return 0

    def tiempoMaximoMin(self):
        # None = sin límite de tiempo. Alimento lo sobrescribe.
        return None

    @abstractmethod
    def recargoCosto(self):
        pass


class Documento(Carga):

    def __init__(self, pesoKg, descripcion, esConfidencial):
        super().__init__(pesoKg, descripcion)
        self.__esConfidencial = bool(esConfidencial)

    @property
    def esConfidencial(self):
        return self.__esConfidencial

    def recargoCosto(self):
        return 1000 if self.__esConfidencial else 0


class Alimento(Carga):

    def __init__(self, pesoKg, descripcion, temperaturaMaxC, tiempoMaxMin):
        super().__init__(pesoKg, descripcion)

        if tiempoMaxMin <= 0:
            raise ValueError("El tiempo máximo debe ser mayor que cero")

        self.__temperaturaMaxC = temperaturaMaxC
        self.__tiempoMaxMin = tiempoMaxMin

    @property
    def temperaturaMaxC(self):
        return self.__temperaturaMaxC

    @property
    def tiempoMaxMin(self):
        return self.__tiempoMaxMin

    def requiereTemperaturaControlada(self):
        return True

    def tiempoMaximoMin(self):
        return self.__tiempoMaxMin

    def recargoCosto(self):
        return 2000


class CargaFragil(Carga):

    def __init__(self, pesoKg, descripcion, nivelFragilidad):
        super().__init__(pesoKg, descripcion)

        if nivelFragilidad not in (1, 2, 3):
            raise ValueError("La fragilidad debe ser 1, 2 o 3")

        self.__nivelFragilidad = nivelFragilidad

    @property
    def nivelFragilidad(self):
        return self.__nivelFragilidad

    def esFragil(self):
        return True

    def nivelRiesgo(self):
        return self.__nivelFragilidad

    def recargoCosto(self):
        return 1500


class MaterialLaboratorio(Carga):

    def __init__(self, pesoKg, descripcion, nivelPeligro, requiereAutorizacion):
        super().__init__(pesoKg, descripcion)

        if nivelPeligro not in (1, 2, 3):
            raise ValueError("El peligro debe ser 1, 2 o 3")

        self.__nivelPeligro = nivelPeligro
        self.__requiereAutorizacion = bool(requiereAutorizacion)

    @property
    def nivelPeligro(self):
        return self.__nivelPeligro

    @property
    def requiereAutorizacion(self):
        return self.__requiereAutorizacion

    def esPeligrosa(self):
        return True

    def nivelRiesgo(self):
        return self.__nivelPeligro

    def recargoCosto(self):
        return 3000

from estados import EstadoRobot, EstadoSolicitud, TipoEvento
from bitacora import BitacoraEventos
from servicio_clima import IServicioClima
from robots import Robot
from solicitudes import SolicitudEntrega


class GestorEntregas:

    def __init__(self, servicioClima):
        if not isinstance(servicioClima, IServicioClima):
            raise TypeError("Se necesita un servicio de clima válido")

        self.__robots = []                      # agregación (0..*)
        self.__solicitudes = []                 # agregación (0..*)
        self.__bitacora = BitacoraEventos()     # composición (1): la crea el gestor
        self.__servicioClima = servicioClima    # asociación (1): se recibe de fuera

    def registrarRobot(self, robot):
        if not isinstance(robot, Robot):
            raise TypeError("Se necesita un robot válido")
        for existente in self.__robots:
            if existente.id == robot.id:
                raise ValueError("Ya existe un robot con el ID " + robot.id)
        self.__robots.append(robot)

    def registrarSolicitud(self, solicitud):
        if not isinstance(solicitud, SolicitudEntrega):
            raise TypeError("Se necesita una solicitud válida")
        for existente in self.__solicitudes:
            if existente.id == solicitud.id:
                raise ValueError("Ya existe una solicitud con el ID " + solicitud.id)
        self.__solicitudes.append(solicitud)

    def __seleccionarRobot(self, solicitud):
        mejor = None
        mejorCosto = None

        for robot in self.__robots:
            if robot.estado != EstadoRobot.DISPONIBLE:
                continue
            if not robot.puedeTransportar(solicitud):
                continue
            if not robot.tieneBateriaPara(solicitud.distanciaKm):
                continue
            # El gestor no sabe qué robot es un dron: solo pregunta.
            if robot.requiereClimaFavorable():
                if not self.__servicioClima.condicionesFavorables(robot.ubicacion):
                    continue

            costo = robot.calcularCosto(solicitud.distanciaKm, solicitud.carga)
            if mejor is None or costo < mejorCosto:
                mejor = robot
                mejorCosto = costo

        return mejor

    def asignar(self, solicitud):
        if solicitud not in self.__solicitudes:
            raise ValueError("La solicitud no está registrada")
        if solicitud.estado != EstadoSolicitud.PENDIENTE:
            raise ValueError("La solicitud no está pendiente")

        robot = self.__seleccionarRobot(solicitud)

        if robot is None:
            self.__bitacora.registrar(
                TipoEvento.ENTREGA_FALLIDA,
                "Sin robot compatible para " + solicitud.id + ": queda pendiente")
            return False

        solicitud.asignarRobot(robot)
        robot.cambiarEstado(EstadoRobot.EN_ENTREGA)
        return True

    def completarEntrega(self, solicitud):
        robot = self.__validarAsignada(solicitud)

        robot.completarViaje(solicitud.distanciaKm, solicitud.destino)
        solicitud.completar()
        robot.cambiarEstado(EstadoRobot.DISPONIBLE)

        self.__bitacora.registrar(
            TipoEvento.ENTREGA_EXITOSA,
            solicitud.id + " entregada por " + robot.id)

    def fallarEntrega(self, solicitud, motivo):
        robot = self.__validarAsignada(solicitud)

        solicitud.marcarFallida(motivo)
        robot.cambiarEstado(EstadoRobot.DISPONIBLE)

        self.__bitacora.registrar(
            TipoEvento.ENTREGA_FALLIDA,
            solicitud.id + " falló con " + robot.id + ": " + motivo)

    def __validarAsignada(self, solicitud):
        if solicitud not in self.__solicitudes:
            raise ValueError("La solicitud no está registrada")
        if solicitud.estado != EstadoSolicitud.ASIGNADA:
            raise ValueError("La solicitud no está asignada")
        return solicitud.robotAsignado

    def estimarEntrega(self, solicitud, robot):
        tiempo = robot.calcularTiempo(solicitud.distanciaKm)
        costo = robot.calcularCosto(solicitud.distanciaKm, solicitud.carga)
        return tiempo, costo

    def registrarMantenimiento(self, robot, detalle):
        if robot not in self.__robots:
            raise ValueError("El robot no está registrado")
        if robot.estado == EstadoRobot.EN_ENTREGA:
            raise ValueError("El robot está en una entrega")
        if not detalle:
            raise ValueError("Indique el detalle del mantenimiento")

        robot.cambiarEstado(EstadoRobot.EN_MANTENIMIENTO)
        self.__bitacora.registrar(TipoEvento.MANTENIMIENTO, robot.id + ": " + detalle)

    def mostrarReporte(self):
        lineas = ["REPORTE DEL SISTEMA", "", "ROBOTS:"]

        for robot in self.__robots:
            lineas.append(robot.id + " | " + robot.estado.value
                          + " | Batería: " + str(round(robot.bateria, 1))
                          + "% | Ubicación: " + robot.ubicacion)

        lineas.extend(["", "SOLICITUDES:"])

        for solicitud in self.__solicitudes:
            lineas.append(solicitud.id + " | " + solicitud.estado.value
                          + " | Carga: " + solicitud.carga.descripcion)

        lineas.extend(["", "BITÁCORA:", self.__bitacora.generarReporte()])

        return "\n".join(lineas)

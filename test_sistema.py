import json
import unittest
from unittest.mock import MagicMock, patch
from urllib.error import URLError

from estados import EstadoRobot, EstadoSolicitud
from robots import Robot, RobotRuedas, RobotOrugas, Dron
from cargas import Carga, Documento, Alimento, CargaFragil, MaterialLaboratorio
from solicitudes import SolicitudEntrega
from gestor import GestorEntregas
from servicio_clima import (IServicioClima, ServicioClimaSimulado,
                            ServicioClimaOpenMeteo)


def armarGestor(clima=None):
    gestor = GestorEntregas(clima or ServicioClimaSimulado(True))
    gestor.registrarRobot(RobotRuedas("R01", 100, "Biblioteca", 10, 5, 2))
    gestor.registrarRobot(RobotOrugas("R02", 80, "Laboratorio", 20, 4, 3, 1.2))
    gestor.registrarRobot(Dron("R03", 90, "Patio", 3, 10, 4, 50))
    return gestor


def respuestaApi(viento, lluvia):
    cuerpo = json.dumps({"current": {"wind_speed_10m": viento},
                         "daily": {"precipitation_probability_max": [lluvia]}})
    falso = MagicMock()
    falso.return_value.__enter__.return_value.read.return_value = cuerpo.encode("utf-8")
    return falso


class PruebasPolimorfismo(unittest.TestCase):

    def test_clases_abstractas_no_se_instancian(self):
        with self.assertRaises(TypeError):
            Robot("X", 100, "A", 1, 1, 1)
        with self.assertRaises(TypeError):
            Carga(1, "x")
        with self.assertRaises(TypeError):
            IServicioClima()

    def test_mismo_mensaje_distinto_resultado_segun_robot(self):
        carga = Documento(1, "Doc", False)
        ruedas = RobotRuedas("R1", 100, "A", 10, 5, 2)
        orugas = RobotOrugas("R2", 100, "A", 10, 5, 2, 1.5)
        dron = Dron("R3", 100, "A", 10, 5, 2, 50)

        robots = [ruedas, orugas, dron]
        tiempos = [r.calcularTiempo(2) for r in robots]
        costos = [r.calcularCosto(2, carga) for r in robots]

        self.assertEqual(tiempos[0], 24)              # 2 / 5 * 60
        self.assertEqual(tiempos[1], 36)              # con factor de terreno 1.5
        self.assertEqual(costos, [1000, 1400, 1600])  # 500, 700, 800 por km

    def test_recargo_segun_tipo_de_carga(self):
        recargos = [Documento(1, "d", True).recargoCosto(),
                    Alimento(1, "a", 5, 30).recargoCosto(),
                    CargaFragil(1, "f", 1).recargoCosto(),
                    MaterialLaboratorio(1, "m", 1, True).recargoCosto()]
        self.assertEqual(recargos, [1000, 2000, 1500, 3000])

    def test_solo_el_dron_exige_clima_y_el_gestor_no_lo_distingue(self):
        self.assertTrue(Dron("D", 100, "A", 1, 1, 1, 10).requiereClimaFavorable())
        self.assertFalse(RobotRuedas("R", 100, "A", 1, 1, 1).requiereClimaFavorable())

    def test_reglas_de_carga_por_tipo_de_robot(self):
        peligroso = MaterialLaboratorio(1, "m", 3, True)
        fragil2 = CargaFragil(1, "f", 2)
        ruedas = RobotRuedas("R1", 100, "A", 10, 5, 1)
        orugas = RobotOrugas("R2", 100, "A", 10, 5, 1, 1)
        dron = Dron("R3", 100, "A", 10, 5, 1, 10)

        self.assertFalse(ruedas.admiteCarga(peligroso))
        self.assertFalse(orugas.admiteCarga(peligroso))     # nivel 3: demasiado
        self.assertTrue(orugas.admiteCarga(fragil2))
        self.assertFalse(ruedas.admiteCarga(fragil2))
        self.assertFalse(dron.admiteCarga(fragil2))


class PruebasEncapsulamiento(unittest.TestCase):

    def test_no_se_puede_modificar_la_bateria_desde_fuera(self):
        robot = RobotRuedas("R1", 100, "A", 10, 5, 2)
        with self.assertRaises(AttributeError):
            robot.bateria = 500
        with self.assertRaises(AttributeError):
            robot.estado = EstadoRobot.EN_ENTREGA

    def test_los_atributos_privados_no_existen_con_su_nombre(self):
        robot = RobotRuedas("R1", 100, "A", 10, 5, 2)
        self.assertFalse(hasattr(robot, "__bateria"))
        carga = Documento(1, "d", False)
        self.assertFalse(hasattr(carga, "__pesoKg"))
        with self.assertRaises(AttributeError):
            carga.pesoKg = 99

    def test_validaciones_internas_en_constructores(self):
        with self.assertRaises(ValueError):
            RobotRuedas("R1", 150, "A", 10, 5, 2)         # batería > 100
        with self.assertRaises(ValueError):
            Documento(-1, "d", False)                      # peso negativo
        with self.assertRaises(ValueError):
            CargaFragil(1, "f", 9)                         # nivel inválido
        with self.assertRaises(ValueError):
            SolicitudEntrega("S", "A", "B", 0, Documento(1, "d", False))

    def test_la_batería_solo_cambia_por_el_comportamiento_del_robot(self):
        robot = RobotRuedas("R1", 100, "A", 10, 5, 2)
        robot.completarViaje(5, "B")
        self.assertEqual(robot.bateria, 90)
        self.assertEqual(robot.ubicacion, "B")
        with self.assertRaises(ValueError):
            robot.completarViaje(1000, "C")                # no alcanza la batería

    def test_robot_en_mantenimiento_no_sale_a_entregar(self):
        robot = RobotRuedas("R1", 100, "A", 10, 5, 2)
        robot.cambiarEstado(EstadoRobot.EN_MANTENIMIENTO)
        with self.assertRaises(ValueError):
            robot.cambiarEstado(EstadoRobot.EN_ENTREGA)


class PruebasAsignacion(unittest.TestCase):

    def test_asignacion_normal_y_robot_de_menor_costo(self):
        gestor = armarGestor()
        s = SolicitudEntrega("S1", "Biblioteca", "Pasillos", 2, Documento(2, "Doc", False))
        gestor.registrarSolicitud(s)
        self.assertTrue(gestor.asignar(s))
        self.assertEqual(s.robotAsignado.id, "R01")        # el más barato
        self.assertEqual(s.estado, EstadoSolicitud.ASIGNADA)
        self.assertEqual(s.robotAsignado.estado, EstadoRobot.EN_ENTREGA)

    def test_reserva_de_bateria(self):
        robot = RobotRuedas("R1", 30, "A", 10, 5, 2)
        self.assertTrue(robot.tieneBateriaPara(5))          # 30 - 10 = 20 (justo)
        self.assertFalse(robot.tieneBateriaPara(6))         # 30 - 12 = 18 < 20

    def test_alimento_respeta_su_tiempo_maximo(self):
        gestor = armarGestor()
        # Ruedas a 5 km/h: 2 km tardan 24 min
        rapido = SolicitudEntrega("S1", "Cafetería", "Pasillos", 2, Alimento(1, "Almuerzo", 60, 30))
        lento = SolicitudEntrega("S2", "Cafetería", "Pasillos", 2, Alimento(1, "Almuerzo", 60, 10))
        gestor.registrarSolicitud(rapido)
        gestor.registrarSolicitud(lento)
        self.assertTrue(gestor.asignar(rapido))
        self.assertFalse(gestor.asignar(lento))             # nadie llega en 10 min

    def test_ids_duplicados_se_rechazan(self):
        gestor = armarGestor()
        with self.assertRaises(ValueError):
            gestor.registrarRobot(RobotRuedas("R01", 100, "A", 10, 5, 2))

    def test_mantenimiento(self):
        gestor = armarGestor()
        robot = RobotRuedas("R9", 100, "A", 10, 5, 2)
        gestor.registrarRobot(robot)
        gestor.registrarMantenimiento(robot, "Cambio de llantas")
        self.assertEqual(robot.estado, EstadoRobot.EN_MANTENIMIENTO)
        self.assertIn("Cambio de llantas", gestor.mostrarReporte())


class PruebasClima(unittest.TestCase):

    def solicitudParaDron(self, id="S1"):
        return SolicitudEntrega(id, "Patio", "Zonas abiertas", 1, Documento(1, "Doc", False))

    def test_clima_malo_rechaza_el_dron_y_la_solicitud_queda_pendiente(self):
        gestor = GestorEntregas(ServicioClimaSimulado(False))
        gestor.registrarRobot(Dron("R03", 90, "Patio", 3, 10, 4, 50))
        s = self.solicitudParaDron()
        gestor.registrarSolicitud(s)
        self.assertFalse(gestor.asignar(s))
        self.assertEqual(s.estado, EstadoSolicitud.PENDIENTE)

    def test_cambiar_de_clima_no_exige_tocar_el_gestor(self):
        s = self.solicitudParaDron()
        for favorable, esperado in ((False, False), (True, True)):
            gestor = GestorEntregas(ServicioClimaSimulado(favorable))
            gestor.registrarRobot(Dron("R03", 90, "Patio", 3, 10, 4, 50))
            solicitud = self.solicitudParaDron()
            gestor.registrarSolicitud(solicitud)
            self.assertEqual(gestor.asignar(solicitud), esperado)

    def test_open_meteo_favorable(self):
        with patch("servicio_clima.urlopen", respuestaApi(10, 20)):
            self.assertTrue(ServicioClimaOpenMeteo().condicionesFavorables("Patio"))

    def test_open_meteo_viento_fuerte(self):
        with patch("servicio_clima.urlopen", respuestaApi(50, 10)):
            self.assertFalse(ServicioClimaOpenMeteo().condicionesFavorables("Patio"))

    def test_open_meteo_lluvia_alta(self):
        with patch("servicio_clima.urlopen", respuestaApi(5, 90)):
            self.assertFalse(ServicioClimaOpenMeteo().condicionesFavorables("Patio"))

    def test_si_la_api_no_responde_no_se_autoriza_el_dron(self):
        with patch("servicio_clima.urlopen", side_effect=URLError("sin internet")):
            self.assertFalse(ServicioClimaOpenMeteo().condicionesFavorables("Patio"))

    def test_si_la_api_devuelve_datos_raros_no_se_autoriza(self):
        falso = MagicMock()
        falso.return_value.__enter__.return_value.read.return_value = b"esto no es json"
        with patch("servicio_clima.urlopen", falso):
            self.assertFalse(ServicioClimaOpenMeteo().condicionesFavorables("Patio"))

    def test_gestor_con_api_caida_deja_la_solicitud_pendiente(self):
        with patch("servicio_clima.urlopen", side_effect=URLError("sin internet")):
            gestor = GestorEntregas(ServicioClimaOpenMeteo())
            gestor.registrarRobot(Dron("R03", 90, "Patio", 3, 10, 4, 50))
            s = self.solicitudParaDron()
            gestor.registrarSolicitud(s)
            self.assertFalse(gestor.asignar(s))
            self.assertEqual(s.estado, EstadoSolicitud.PENDIENTE)


class PruebasBitacora(unittest.TestCase):

    def test_entrega_exitosa_actualiza_robot_y_bitacora(self):
        gestor = armarGestor()
        s = SolicitudEntrega("S1", "Biblioteca", "Pasillos", 2, Documento(2, "Doc", False))
        gestor.registrarSolicitud(s)
        gestor.asignar(s)
        robot = s.robotAsignado
        gestor.completarEntrega(s)
        self.assertEqual(s.estado, EstadoSolicitud.COMPLETADA)
        self.assertEqual(robot.estado, EstadoRobot.DISPONIBLE)
        self.assertEqual(robot.ubicacion, "Pasillos")
        self.assertEqual(robot.bateria, 96)                 # 100 - 2 km * 2
        self.assertIn("Entrega exitosa", gestor.mostrarReporte())

    def test_entrega_fallida_queda_en_la_bitacora(self):
        gestor = armarGestor()
        s = SolicitudEntrega("S1", "Biblioteca", "Pasillos", 2, Documento(2, "Doc", False))
        gestor.registrarSolicitud(s)
        gestor.asignar(s)
        gestor.fallarEntrega(s, "Obstáculo en el pasillo")
        self.assertEqual(s.estado, EstadoSolicitud.FALLIDA)
        self.assertIn("Obstáculo en el pasillo", gestor.mostrarReporte())

    def test_no_se_completa_una_solicitud_sin_asignar(self):
        gestor = armarGestor()
        s = SolicitudEntrega("S1", "Biblioteca", "Pasillos", 2, Documento(2, "Doc", False))
        gestor.registrarSolicitud(s)
        with self.assertRaises(ValueError):
            gestor.completarEntrega(s)


if __name__ == "__main__":
    unittest.main(verbosity=2)

from robots import RobotRuedas, RobotOrugas, Dron
from cargas import Documento, Alimento, MaterialLaboratorio
from solicitudes import SolicitudEntrega
from gestor import GestorEntregas
from servicio_clima import ServicioClimaSimulado, ServicioClimaOpenMeteo

# Cambiar a True para consultar la API real de Open-Meteo (requiere internet).
# Es lo ÚNICO que hay que tocar para cambiar de proveedor: el gestor no cambia.
USAR_API_REAL = False

clima = ServicioClimaOpenMeteo() if USAR_API_REAL else ServicioClimaSimulado(True)
gestor = GestorEntregas(clima)

gestor.registrarRobot(RobotRuedas("R01", 100, "Biblioteca", 10, 5, 2))
gestor.registrarRobot(RobotOrugas("R02", 80, "Laboratorio", 20, 4, 3, 1.2))
gestor.registrarRobot(Dron("R03", 90, "Patio", 3, 10, 4, 50))

# La carga se crea dentro de la solicitud: composición.
s1 = SolicitudEntrega("S01", "Biblioteca", "Pasillos", 2,
                      Documento(2, "Documentos universitarios", False))
s2 = SolicitudEntrega("S02", "Cafetería", "Zonas abiertas", 1.5,
                      Alimento(1, "Almuerzo", 60, 30))
s3 = SolicitudEntrega("S03", "Laboratorio", "Zonas verdes", 1,
                      MaterialLaboratorio(2, "Reactivos", 3, True))

for solicitud in (s1, s2, s3):
    gestor.registrarSolicitud(solicitud)

for solicitud in (s1, s2, s3):
    if gestor.asignar(solicitud):
        robot = solicitud.robotAsignado
        tiempo, costo = gestor.estimarEntrega(solicitud, robot)
        print(solicitud.id, "->", robot.id,
              "| tiempo:", round(tiempo, 1), "min | costo:", costo)
        gestor.completarEntrega(solicitud)
    else:
        print(solicitud.id, "-> sin robot compatible, queda pendiente")

print()
print(gestor.mostrarReporte())

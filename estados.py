from enum import Enum


class EstadoRobot(Enum):
    DISPONIBLE = "Disponible"
    EN_ENTREGA = "En entrega"
    EN_MANTENIMIENTO = "En mantenimiento"


class EstadoSolicitud(Enum):
    PENDIENTE = "Pendiente"
    ASIGNADA = "Asignada"
    COMPLETADA = "Completada"
    FALLIDA = "Fallida"


class TipoEvento(Enum):
    ENTREGA_EXITOSA = "Entrega exitosa"
    ENTREGA_FALLIDA = "Entrega fallida"
    MANTENIMIENTO = "Mantenimiento"
    
    
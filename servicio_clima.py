import json
from abc import ABC, abstractmethod
from urllib.parse import urlencode
from urllib.request import urlopen

# Coordenadas aproximadas del campus (Medellín). Ajustar si se necesita más precisión.
COORDENADAS_CAMPUS = (6.2442, -75.5812)
TIEMPO_ESPERA_SEG = 5


class ErrorServicioClima(Exception):
    """La API de clima no respondió o devolvió datos inesperados."""


class IServicioClima(ABC):

    @abstractmethod
    def condicionesFavorables(self, ubicacion):
        pass


class ServicioClimaSimulado(IServicioClima):

    def __init__(self, favorable=True):
        self.__favorable = favorable

    def condicionesFavorables(self, ubicacion):
        return self.__favorable


class ServicioClimaOpenMeteo(IServicioClima):

    def __init__(self, urlBase="https://api.open-meteo.com/v1/forecast",
                 umbralVientoKmh=35, umbralLluviaPct=60):
        if not urlBase:
            raise ValueError("La URL base es obligatoria")
        if umbralVientoKmh < 0 or not 0 <= umbralLluviaPct <= 100:
            raise ValueError("Umbrales inválidos")

        self.__urlBase = urlBase
        self.__umbralVientoKmh = umbralVientoKmh
        self.__umbralLluviaPct = umbralLluviaPct

    def __consultarApi(self, ubicacion):
        # Un solo campus: se usan coordenadas fijas y se ignora el nombre de la zona.
        latitud, longitud = COORDENADAS_CAMPUS
        parametros = urlencode({
            "latitude": latitud,
            "longitude": longitud,
            "current": "wind_speed_10m",
            "daily": "precipitation_probability_max",
            "forecast_days": 1,
            "timezone": "auto",
        })

        try:
            with urlopen(self.__urlBase + "?" + parametros,
                         timeout=TIEMPO_ESPERA_SEG) as respuesta:
                datos = json.loads(respuesta.read().decode("utf-8"))

            return {
                "vientoKmh": float(datos["current"]["wind_speed_10m"]),
                "lluviaPct": float(datos["daily"]["precipitation_probability_max"][0]),
            }
        except (OSError, ValueError, KeyError, IndexError, TypeError) as error:
            raise ErrorServicioClima("No se pudo consultar Open-Meteo: " + str(error)) from error

    def condicionesFavorables(self, ubicacion):
        # Si la API falla, por seguridad NO se autorizan los drones.
        try:
            datos = self.__consultarApi(ubicacion)
        except ErrorServicioClima:
            return False

        return (datos["vientoKmh"] <= self.__umbralVientoKmh
                and datos["lluviaPct"] <= self.__umbralLluviaPct)

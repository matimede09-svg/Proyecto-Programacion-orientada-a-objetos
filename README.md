#  Sistema de Gestión de Flota de Robots Universitarios

Este es nuestro proyecto final para la materia de Programación Orientada a Objetos. Hemos construido el núcleo de un sistema para administrar entregas en un campus universitario utilizando distintos tipos de robots (Drones, Orugas, Ruedas) y diferentes tipos de cargas.

Todo está programado en Python utilizando únicamente la biblioteca estándar. 

##  Cómo ejecutar el proyecto 

1. **Para ver la simulación principal:**
   * Abre el archivo `main.py`.
   * Haz clic en el botón de Play (o presiona `F5`).
   * En la consola de IPython (abajo a la derecha) verás cómo se registran las solicitudes, cómo se asignan los robots, el cálculo de tiempos/costos y el reporte final de la bitácora.

2. **Para correr la batería de pruebas:**
   * Abre el archivo `test_sistema.py` en Spyder y dale al botón de **Play**.
   * *Alternativa:* En la consola IPython de Spyder, puedes escribir directamente: 
     `!python -m unittest test_sistema -v`
   * Verás un reporte detallado (OK) demostrando que el polimorfismo, la integración de la API y el encapsulamiento funcionan a la perfección.

##  Cambiando el clima (La integración con la API)

Una de las mejores características de nuestro diseño es que aislamos por completo la conexión a internet del resto del programa (Principio de Inversión de Dependencias).

Si abres el archivo `main.py`, en las primeras líneas verás esto:
```python
USAR_API_REAL = False
```

* **Déjalo en `False`** si quieres correr el simulador interno (ideal para probar rápido sin conexión).
* **Cámbialo a `True`** y vuelve a darle Play. El sistema se conectará en tiempo real a la API de Open-Meteo para revisar la velocidad del viento y la lluvia antes de autorizar a los drones. Si no hay internet, el sistema lo maneja con gracia y deja los drones en tierra.

##  Organización del código

Decidimos separar las responsabilidades en distintos archivos para mantener una alta cohesión:

* `estados.py`: Contiene nuestras enumeraciones (`Enum`). Evita que alguien invente estados inválidos por errores de tipeo.
* `cargas.py`: Nuestro catálogo de paquetes. Aquí vive la clase abstracta `Carga` y todas sus especializaciones (Documentos, Alimentos, etc.).
* `robots.py`: El corazón del transporte. Define cómo los diferentes robots calculan sus tiempos, costos y reglas de carga.
* `solicitudes.py`: Une un origen, un destino, una carga y, posteriormente, un robot asignado.
* `bitacora.py`: Nuestro pequeño historiador; anota todo lo que sale bien o mal en el sistema.
* `servicio_clima.py`: Contiene la interfaz abstracta del clima y la conexión real a Open-Meteo.
* `gestor.py`: El `GestorEntregas`, la clase principal que coordina a los robots y las solicitudes.


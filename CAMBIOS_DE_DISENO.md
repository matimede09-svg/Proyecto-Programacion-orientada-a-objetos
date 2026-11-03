# Anexo: Cambios de diseño 
*(Del UML de la Fase 3 al código final de la Fase 5)*

Durante la etapa de programación, nos dimos cuenta de que algunas ideas que planteamos en nuestro diagrama UML necesitaban evolucionar. Para respetar verdaderamente los principios de la Programación Orientada a Objetos (POO), implementamos los siguientes ajustes técnicos y de lógica:

### A. Ajustes técnicos y de POO

*   **Implementamos `@property` para leer datos clave de forma segura:**
    *   *¿Qué pasó?* En el UML marcamos atributos (como la batería o el estado del robot) como privados. Pero en la práctica, el Gestor necesitaba conocer esos datos para tomar decisiones.
    *   *¿Qué aprendimos?* En lugar de volverlos públicos (lo cual rompería el encapsulamiento), creamos propiedades de solo lectura. Así, el Gestor puede "mirar" la batería, pero no puede alterarla por accidente.

*   **Creamos el método `completarViaje()` en la clase Robot:**
    *   *¿Qué pasó?* Al principio, era la clase `SolicitudEntrega` la que entraba y le restaba la batería al robot cuando el viaje terminaba. 
    *   *¿Qué aprendimos?* Nos dimos cuenta de que un objeto estaba modificando directamente el estado de otro. Para lograr un encapsulamiento real, ahora se le avisa al robot que el viaje terminó, y él mismo se encarga de descontar su propia batería.

*   **Se eliminó el uso de isinstance() para evaluar las cargas:**
    *   *¿Qué pasó?* En nuestros primeros borradores, los robots usaban una cadena de condicionales `if` para preguntar si la carga era un `Alimento` o un `Documento`. 
    *   *¿Qué aprendimos?* Esto violaba el principio Abierto/Cerrado (OCP), porque si agregábamos un paquete nuevo, teníamos que editar a los robots. Aplicamos polimorfismo: creamos métodos como `esPeligrosa()` o `esFragil()` en la Carga. Ahora el robot simplemente pregunta, y la carga responde por sí misma.

*   **Cambiamos los simples `print` por Excepciones reales (`ValueError`/`TypeError`):**
    *   *¿Qué pasó?* Cuando ingresábamos un dato inválido (como un peso negativo), el código imprimía un mensaje en consola, pero seguía ejecutándose y fallaba más adelante de forma silenciosa.
    *   *¿Qué aprendimos?* Lanzar excepciones hace que el programa frene donde debe, protegiendo la integridad de los datos y haciendo que nuestras pruebas unitarias sean mucho más fáciles de escribir.

*   **Manejamos las caídas de internet en la API de Clima:**
    *   *¿Qué pasó?* Teníamos que resolver qué hacer si la API de Open-Meteo no respondía. 
    *   *¿Qué aprendimos?* Creamos una excepción personalizada `ErrorServicioClima`. Si el internet falla, la clase del clima atrapa el error y simplemente devuelve `False` (rechazando el vuelo por seguridad). El gestor no depende de Open-Meteo ni de los errores de red, lo que mantiene bajo el acoplamiento entre ambos.

### B. Ajustes en las reglas de negocio
*(Decidimos hacer estos ajustes funcionales para darle un comportamiento más lógico y realista a nuestra flota)*

*     **Los alimentos ya no son exclusivos de los drones:** Originalmente, pensamos que solo los drones llevarían comida. Pero si llovía, la comida nunca llegaba. Decidimos que cualquier robot terrestre puede llevar alimentos, siempre y cuando llegue antes del tiempo máximo permitido para que no se enfríen.
*   **Flexibilidad con el Material de Laboratorio:** Ahora los robots de orugas aceptan químicos si su nivel de peligro es 1 o 2. Decidimos quitar el requisito de la "autorización", asumiendo que ese papeleo se hace fuera del sistema.
*   **Optimizando la economía de la universidad:** Si hay varios robots disponibles que pueden hacer un mismo viaje, nuestro Gestor ahora calcula cuánto cobraría cada uno y elige al más económico, en lugar de asignar simplemente al primero que encuentre en la lista.
*   **Reserva de batería estricta:** Para cuidar los equipos, programamos que ningún robot acepte un viaje si sus cálculos le indican que terminará con menos del 20% de batería.
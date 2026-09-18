# Diseño de la cola de triaje

## Estructura elegida

`TriageQueue` utiliza tres `collections.deque`, una para cada nivel de prioridad. `dequeue()` y `peek()` revisan las colas en el orden 1, 2 y 3; cada `deque` conserva el orden FIFO de los pacientes del mismo nivel.

Esta elección evita reordenar toda la cola cuando llega un paciente crítico: se añade directamente al final de la cola de nivel 1 y será atendido antes que los niveles inferiores.

## Alternativas

- **Una sola `deque`**: es eficiente para extremos, pero no inserta un paciente crítico en su posición correcta sin recorrer o reconstruir la cola.
- **Lista ordenada**: es sencilla de consultar, pero insertar en el centro cuesta `O(n)` y puede implicar desplazar muchos elementos.
- **Tres colas separadas**: es la solución adoptada; ofrece operaciones simples y eficientes, aunque requiere consultar tres estructuras.
- **Heap de prioridad**: permite insertar y extraer prioridades en `O(log n)`, pero necesita un contador de secuencia para garantizar FIFO dentro del mismo nivel y hace que recorrer la cola en orden sea más complejo.

## Complejidad

Sea `n` el número de pacientes pendientes:

- `enqueue`: `O(1)`.
- `dequeue`: `O(1)`, porque solo se revisan como máximo tres colas.
- `peek`: `O(1)`.
- `list_queue`: `O(n)` para crear la instantánea.
- `stats`: `O(1)`, al existir siempre tres niveles.

## Concurrencia

Las operaciones que leen o modifican las tres colas están protegidas por `threading.Lock`. En un sistema con workers, `dequeue()` debe adquirir el lock, comprobar los niveles en orden, retirar exactamente un paciente y liberar el lock antes de procesarlo. `enqueue()` debe adquirir el mismo lock y añadir completamente el paciente a su `deque` antes de liberarlo.

Así, un paciente crítico que llegue mientras otro worker extrae un paciente no puede observar ni dejar un estado parcial. La extracción es atómica: un único worker recibe el paciente retirado y ningún otro puede procesarlo. El nuevo paciente crítico queda disponible para la siguiente extracción, respetando la prioridad sin perder entradas ni procesar dos veces el mismo paciente.

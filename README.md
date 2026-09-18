# HUGO-VC-triage-queue

Gestor de cola de prioridad para el triaje de pacientes, implementado con la
biblioteca estándar de Python.

## Uso

```bash
python3 triage_queue.py
```

El menú permite añadir pacientes, llamar al siguiente paciente, consultar la
cola y ver estadísticas por nivel. Los niveles son:

- `1`: crítico
- `2`: urgente
- `3`: estándar

Los pacientes se atienden por prioridad y, dentro del mismo nivel, en orden
FIFO. Consulta [DESIGN.md](DESIGN.md) para conocer las decisiones técnicas.

## Pruebas

```bash
python3 -m unittest -v
```
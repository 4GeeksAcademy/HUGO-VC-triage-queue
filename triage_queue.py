"""Gestor de cola de prioridad para el triaje de pacientes."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from datetime import datetime
from threading import Lock
from typing import Deque, Dict, List


@dataclass(frozen=True)
class Patient:
	"""Representa a un paciente pendiente de atención."""

	name: str
	triage_level: int
	arrived_at: datetime = field(default_factory=datetime.now)

	def __post_init__(self) -> None:
		if not isinstance(self.name, str) or not self.name.strip():
			raise ValueError("El nombre del paciente no puede estar vacío.")
		if self.triage_level not in (1, 2, 3):
			raise ValueError("El nivel de triaje debe ser 1, 2 o 3.")
		if not isinstance(self.arrived_at, datetime):
			raise TypeError("arrived_at debe ser un objeto datetime.")


class TriageQueue:
	"""Cola de prioridad con FIFO independiente para cada nivel."""

	def __init__(self) -> None:
		self._queues: Dict[int, Deque[Patient]] = {
			1: deque(),
			2: deque(),
			3: deque(),
		}
		self._lock = Lock()

	def enqueue(self, patient: Patient) -> None:
		"""Añade ``patient`` al final de su cola de prioridad."""
		if not isinstance(patient, Patient):
			raise TypeError("Solo se pueden encolar objetos Patient.")
		# La mutación está protegida para que enqueue sea atómica frente a
		# dequeue/list_queue/stats en un posible uso desde varios workers.
		with self._lock:
			self._queues[patient.triage_level].append(patient)

	def dequeue(self) -> Patient:
		"""Extrae el paciente de mayor prioridad que lleve más tiempo esperando."""
		with self._lock:
			for level in (1, 2, 3):
				if self._queues[level]:
					return self._queues[level].popleft()
		raise IndexError("No hay pacientes en espera.")

	def peek(self) -> Patient:
		"""Devuelve el siguiente paciente sin retirarlo de la cola."""
		with self._lock:
			for level in (1, 2, 3):
				if self._queues[level]:
					return self._queues[level][0]
		raise IndexError("No hay pacientes en espera.")

	def list_queue(self) -> List[Patient]:
		"""Devuelve una instantánea de la cola en orden de atención."""
		with self._lock:
			return [
				patient
				for level in (1, 2, 3)
				for patient in self._queues[level]
			]

	def stats(self) -> Dict[int, int]:
		"""Devuelve el número de pacientes pendientes por nivel."""
		with self._lock:
			return {level: len(self._queues[level]) for level in (1, 2, 3)}


def _ask_patient() -> Patient:
	"""Solicita y valida los datos de un paciente desde la terminal."""
	while True:
		name = input("Nombre del paciente: ").strip()
		if name:
			break
		print("El nombre no puede estar vacío.")

	while True:
		value = input("Nivel de triaje (1 crítico, 2 urgente, 3 estándar): ").strip()
		try:
			level = int(value)
			return Patient(name=name, triage_level=level)
		except (TypeError, ValueError):
			print("Introduce un nivel válido: 1, 2 o 3.")


def main() -> None:
	"""Ejecuta el menú interactivo del gestor de triaje."""
	queue = TriageQueue()
	actions = {
		"1": "Añadir paciente",
		"2": "Llamar al siguiente paciente",
		"3": "Ver cola actual",
		"4": "Ver estadísticas",
		"5": "Salir",
	}

	while True:
		print("\n=== Cola de triaje ===")
		for key, label in actions.items():
			print(f"{key}. {label}")
		option = input("Selecciona una opción: ").strip()

		if option == "1":
			try:
				patient = _ask_patient()
				queue.enqueue(patient)
				print(f"Paciente añadido: {patient.name} (nivel {patient.triage_level}).")
			except (EOFError, KeyboardInterrupt):
				print("\nEntrada cancelada.")
		elif option == "2":
			try:
				patient = queue.dequeue()
				print(f"Siguiente paciente: {patient.name} (nivel {patient.triage_level}).")
			except IndexError as error:
				print(error)
		elif option == "3":
			patients = queue.list_queue()
			if not patients:
				print("No hay pacientes en espera.")
			else:
				for position, patient in enumerate(patients, start=1):
					print(f"{position}. {patient.name} - nivel {patient.triage_level}")
		elif option == "4":
			statistics = queue.stats()
			print("Estadísticas: " + ", ".join(
				f"nivel {level}: {count}" for level, count in statistics.items()
			))
		elif option == "5":
			print("Hasta pronto.")
			break
		else:
			print("Opción no válida. Selecciona un número del 1 al 5.")


if __name__ == "__main__":
	main()

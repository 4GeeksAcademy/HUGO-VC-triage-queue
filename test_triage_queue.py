import unittest
from datetime import datetime

from triage_queue import Patient, TriageQueue


class TriageQueueTests(unittest.TestCase):
    def setUp(self):
        self.queue = TriageQueue()

    def test_priority_and_fifo(self):
        self.queue.enqueue(Patient("Urgente 1", 2))
        self.queue.enqueue(Patient("Estándar", 3))
        self.queue.enqueue(Patient("Crítico", 1))
        self.queue.enqueue(Patient("Urgente 2", 2))

        self.assertEqual(
            [patient.name for patient in self.queue.list_queue()],
            ["Crítico", "Urgente 1", "Urgente 2", "Estándar"],
        )

    def test_peek_does_not_remove(self):
        patient = Patient("Ana", 1)
        self.queue.enqueue(patient)

        self.assertIs(self.queue.peek(), patient)
        self.assertEqual(self.queue.stats(), {1: 1, 2: 0, 3: 0})

    def test_dequeue_removes_next_patient(self):
        first = Patient("Primero", 2)
        second = Patient("Segundo", 2)
        self.queue.enqueue(first)
        self.queue.enqueue(second)

        self.assertIs(self.queue.dequeue(), first)
        self.assertIs(self.queue.peek(), second)

    def test_empty_queue_operations_raise_descriptive_error(self):
        with self.assertRaisesRegex(IndexError, "No hay pacientes"):
            self.queue.dequeue()
        with self.assertRaisesRegex(IndexError, "No hay pacientes"):
            self.queue.peek()

    def test_invalid_triage_level_is_rejected(self):
        with self.assertRaises(ValueError):
            Patient("Paciente", 4)
        with self.assertRaises(ValueError):
            Patient("Paciente", 0)

    def test_equal_timestamps_keep_enqueue_order(self):
        timestamp = datetime(2026, 1, 1)
        first = Patient("Primero", 1, timestamp)
        second = Patient("Segundo", 1, timestamp)
        self.queue.enqueue(first)
        self.queue.enqueue(second)

        self.assertEqual(self.queue.dequeue(), first)
        self.assertEqual(self.queue.dequeue(), second)


if __name__ == "__main__":
    unittest.main()

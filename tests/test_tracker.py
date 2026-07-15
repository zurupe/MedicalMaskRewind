import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from detector_mascarillas import SimpleTracker
from logger import BioseguridadLogger


class TrackerTests(unittest.TestCase):
    def test_tracker_counts_stationary_person_once(self):
        tracker = SimpleTracker(max_missed=3)

        detections = [
            (0, (10, 20, 100, 120)),
            (0, (10, 20, 100, 120)),
            (0, (10, 20, 100, 120)),
        ]

        tracked = tracker.update(detections)
        self.assertEqual(len(tracked), 1)

        counts = tracker.get_counts()
        self.assertEqual(counts["total"], 1)
        self.assertEqual(counts["con_mascarilla"], 1)
        self.assertEqual(counts["sin_mascarilla"], 0)

    def test_logger_exposes_detection_and_tracked_metrics(self):
        logger = BioseguridadLogger(
            filename="test_registro.txt",
            state_filename="test_state.json",
            db_path="test_bioseguridad.db",
        )

        result = logger.registrar(
            total=2,
            con_mascarilla=1,
            sin_mascarilla=1,
            incorrecta=0,
            detecciones_modelo=5,
            personas_reales=2,
        )

        self.assertEqual(result["detecciones_modelo"], 5)
        self.assertEqual(result["personas_reales"], 2)


if __name__ == '__main__':
    unittest.main()

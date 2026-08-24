"""Regression coverage for the documented untreated legacy trajectory."""

import hashlib
import unittest

import numpy as np

from tumor_ca import AdvancedTumorCA


def run_untreated(seed):
    """Run the small, seeded legacy setup without therapy."""
    ca = AdvancedTumorCA(size=9, seed=seed)
    ca.initialize_tumor(radius=1, normal_cells=False)
    ca.therapy.fill(0.0)

    for _ in range(6):
        ca.step()

    return ca


class LegacyUntreatedTrajectoryTests(unittest.TestCase):
    def test_seeded_trajectory_and_replay_match_legacy_behavior(self):
        first = run_untreated(seed=7)
        replay = run_untreated(seed=7)

        self.assertEqual(
            tuple(first.history["total_tumor"]),
            (10, 20, 33, 50, 70, 80),
        )
        self.assertEqual(tuple(first.history["resistant"]), (0, 0, 0, 0, 0, 0))
        self.assertEqual(tuple(first.history["dead"]), (0, 0, 0, 0, 0, 0))
        self.assertTrue(np.array_equal(first.grid, replay.grid))
        self.assertEqual(
            hashlib.sha256(first.grid.tobytes()).hexdigest(),
            "1476bf9e047d5d4649a0a3ba959f6131a3f089483dedc9dbb1d60422be0246c0",
        )

    def test_untreated_trajectory_remains_seed_sensitive(self):
        seed_seven = run_untreated(seed=7)
        seed_eight = run_untreated(seed=8)

        self.assertFalse(np.array_equal(seed_seven.grid, seed_eight.grid))


if __name__ == "__main__":
    unittest.main()

"""Run: python3 -m unittest -v test_planner.py"""
import io
import math
import sys
import unittest
from contextlib import redirect_stderr, redirect_stdout
from unittest.mock import patch

import planner


class CCTVPlanTests(unittest.TestCase):
    def test_readme_scenario(self):
        plan = planner.CCTVPlan(8, 4096, 15, 24, 8)
        self.assertAlmostEqual(plan.total_bandwidth_mbps, 32.768)
        self.assertAlmostEqual(plan.storage_tb, 5.308416)
        self.assertEqual(plan.recommended_disk_tb, 6)
        self.assertAlmostEqual(plan.poe_budget_watts, 76.8)

    def test_no_recording_more_than_24_hours_per_day(self):
        with self.assertRaisesRegex(ValueError, "cannot exceed 24"):
            planner.CCTVPlan(8, 4096, 15, 25, 8)

    def test_reject_bad_camera_count(self):
        for count in (0, -1, True, 1.5):
            with self.subTest(count=count), self.assertRaises(ValueError):
                planner.CCTVPlan(count, 4096, 15, 24, 8)

    def test_reject_invalid_measurements(self):
        for name in ("bitrate_kbps", "days", "hours_per_day", "poe_watts"):
            for bad in (0, -1, math.inf, -math.inf, math.nan):
                with self.subTest(name=name, bad=bad), self.assertRaises(ValueError):
                    values = dict(cameras=8, bitrate_kbps=4096, days=15,
                                  hours_per_day=24, poe_watts=8)
                    values[name] = bad
                    planner.CCTVPlan(**values)

    def test_negative_or_nonfinite_overhead(self):
        for bad in (-1, math.inf, math.nan):
            with self.subTest(bad=bad), self.assertRaises(ValueError):
                planner.CCTVPlan(8, 4096, 15, 24, 8, bad)

    def test_reject_computational_overflow(self):
        with self.assertRaisesRegex(ValueError, "too large"):
            planner.CCTVPlan(8, 1e308, 15, 24, 8)

    def test_custom_headroom(self):
        self.assertAlmostEqual(planner.CCTVPlan(2, 1000, 1, 24, 10, 30).poe_budget_watts, 26)

    def test_cli_rejects_invalid_input_without_traceback(self):
        args = ["planner.py", "--cameras", "0", "--bitrate-kbps", "4096",
                "--days", "15", "--hours-per-day", "24", "--poe-watts", "8"]
        with patch.object(sys, "argv", args), redirect_stderr(io.StringIO()) as err:
            with self.assertRaises(SystemExit) as cm:
                planner.main()
        self.assertEqual(cm.exception.code, 2)
        self.assertIn("positive integer", err.getvalue())
        self.assertNotIn("Traceback", err.getvalue())

    def test_cli_valid_output(self):
        args = ["planner.py", "--cameras", "8", "--bitrate-kbps", "4096",
                "--days", "15", "--hours-per-day", "24", "--poe-watts", "8"]
        with patch.object(sys, "argv", args), redirect_stdout(io.StringIO()) as out:
            self.assertEqual(planner.main(), 0)
        self.assertIn("Total bandwidth: 32.77 Mbps", out.getvalue())


if __name__ == "__main__":
    unittest.main()

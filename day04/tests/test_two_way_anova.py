import math
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from two_way_anova import analyze


def f_1_4_survival(f_statistic: float) -> float:
    # Closed-form upper-tail probability for an F distribution with (1, 4) df.
    ratio = f_statistic / (f_statistic + 4)
    root = math.sqrt(ratio)
    return 1 - 1.5 * root + 0.5 * root**3


class TwoWayAnovaTests(unittest.TestCase):
    def test_analyze_matches_independently_derived_balanced_anova(self):
        data = [
            {"Group": group, "Treatment": treatment, "Measurement": value}
            for group, treatment, measurements in (
                ("G1", "T1", (1, 2)),
                ("G1", "T2", (3, 4)),
                ("G2", "T1", (5, 6)),
                ("G2", "T2", (9, 10)),
            )
            for value in measurements
        ]

        results = analyze(data)

        # Directly from the cell means (1.5, 3.5, 5.5, 9.5):
        # SS_group=50, SS_treatment=18, SS_interaction=2, and SS_error=2.
        # There are 4 error degrees of freedom, so MSE=0.5.
        effect_sum_squares = (
            ("Group", 50),
            ("Treatment", 18),
            ("Group x Treatment", 2),
        )
        expected = tuple(
            (
                label,
                sum_squares / 0.5,
                f_1_4_survival(sum_squares / 0.5),
                sum_squares / (sum_squares + 2),
            )
            for label, sum_squares in effect_sum_squares
        )
        self.assertEqual(
            tuple(result[0] for result in results),
            tuple(result[0] for result in expected),
        )
        for actual, expected_result in zip(results, expected):
            for actual_value, expected_value in zip(actual[1:], expected_result[1:]):
                self.assertAlmostEqual(actual_value, expected_value, places=10)

    def test_analyze_rejects_data_without_residual_degrees_of_freedom(self):
        data = [
            {"Group": group, "Treatment": treatment, "Measurement": value}
            for (group, treatment), value in zip(
                (("G1", "T1"), ("G1", "T2"), ("G2", "T1"), ("G2", "T2")),
                (1, 2, 3, 4),
            )
        ]

        with self.assertRaisesRegex(ValueError, "not enough measurements"):
            analyze(data)


if __name__ == "__main__":
    unittest.main()

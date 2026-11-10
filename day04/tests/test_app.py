import unittest

from app import app


class AnovaWebAppTests(unittest.TestCase):
    def setUp(self) -> None:
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_home_page_shows_factor_inputs_and_measurement_fields(self):
        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertIn(b'name="groups"', response.data)
        self.assertIn(b'name="treatments"', response.data)
        self.assertIn(b"Run ANOVA", response.data)

    def test_valid_measurements_show_anova_results(self):
        response = self.client.post(
            "/",
            data={
                "groups": "Control, Knockout",
                "treatments": "Vehicle, Drug",
                "measurement_0": "1, 2",
                "measurement_1": "2, 3",
                "measurement_2": "3, 4",
                "measurement_3": "6, 8",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn(b"ANOVA results (Type II sums of squares)", response.data)
        self.assertIn(b"Group x Treatment", response.data)

    def test_missing_measurement_shows_validation_error(self):
        response = self.client.post(
            "/",
            data={
                "groups": "Control, Knockout",
                "treatments": "Vehicle, Drug",
                "measurement_0": "1, 2",
                "measurement_1": "2, 3",
                "measurement_2": "3, 4",
                "measurement_3": "",
            },
        )

        self.assertIn(b"Enter at least one measurement", response.data)

    def test_duplicate_factor_names_are_rejected(self):
        response = self.client.post(
            "/",
            data={
                "groups": "Control, Control",
                "treatments": "Vehicle, Drug",
            },
        )

        self.assertIn(b"Group names must be unique", response.data)


if __name__ == "__main__":
    unittest.main()

"""Flask interface for the two-way ANOVA implementation."""

import math

from flask import Flask, render_template, request

from two_way_anova import analyze

app = Flask(__name__)

DEFAULT_GROUPS = "Control, Knockout"
DEFAULT_TREATMENTS = "Vehicle, Drug"


def parse_names(value: str, factor: str) -> list[str]:
    names = [name.strip() for name in value.split(",") if name.strip()]
    if len(names) < 2:
        raise ValueError(f"Enter at least two {factor} names.")
    if len(names) != len(set(names)):
        raise ValueError(f"{factor.capitalize()} names must be unique.")
    return names


def render_page(
    groups_value: str,
    treatments_value: str,
    measurements: list[str],
    results: list[dict[str, str]] | None = None,
    error: str | None = None,
) -> str:
    return render_template(
        "index.html",
        groups_value=groups_value,
        treatments_value=treatments_value,
        measurements=measurements,
        results=results,
        error=error,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_page(DEFAULT_GROUPS, DEFAULT_TREATMENTS, [])

    groups_value = request.form.get("groups", "")
    treatments_value = request.form.get("treatments", "")
    groups: list[str] = []
    treatments: list[str] = []
    measurements: list[str] = []
    results = None
    error = None

    try:
        groups = parse_names(groups_value, "group")
        treatments = parse_names(treatments_value, "treatment")
        data: list[dict[str, str | float]] = []
        measurements = [
            request.form.get(f"measurement_{index}", "")
            for index in range(len(groups) * len(treatments))
        ]

        combinations = (
            (group, treatment)
            for group in groups
            for treatment in treatments
        )
        for field_index, (group, treatment) in enumerate(combinations):
            raw_values = measurements[field_index]
            values = [
                value.strip()
                for value in raw_values.replace("\n", ",").split(",")
                if value.strip()
            ]
            if not values:
                raise ValueError(
                    f"Enter at least one measurement for "
                    f"{group} / {treatment}."
                )

            for value in values:
                try:
                    measurement = float(value)
                except ValueError as parse_error:
                    raise ValueError(
                        f"'{value}' is not a valid number for "
                        f"{group} / {treatment}."
                    ) from parse_error
                if not math.isfinite(measurement):
                    raise ValueError(
                        f"Measurements must be finite numbers "
                        f"({group} / {treatment})."
                    )
                data.append(
                    {
                        "Group": group,
                        "Treatment": treatment,
                        "Measurement": measurement,
                    }
                )

        effects = analyze(data)
        results = [
            {
                "source": source,
                "f_statistic": f"{f_statistic:.6g}",
                "p_value": f"{p_value:.6g}",
                "partial_eta_squared": f"{eta_squared:.6g}",
            }
            for source, f_statistic, p_value, eta_squared in effects
        ]
    except ValueError as exception:
        error = str(exception)

    return render_page(
        groups_value,
        treatments_value,
        measurements,
        results=results,
        error=error,
    )


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)

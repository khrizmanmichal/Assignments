"""Run a two-way ANOVA on independent group and treatment measurements."""

import math

import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


def ask_name(prompt: str) -> str:
    while True:
        name = input(prompt).strip()
        if name:
            return name
        print("Please enter a non-empty name.")


def ask_count(prompt: str, minimum: int = 1) -> int:
    while True:
        value = input(prompt).strip()
        try:
            count = int(value)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if count < minimum:
            print(f"Please enter a number of at least {minimum}.")
            continue
        return count


def ask_names(label: str, count: int) -> list[str]:
    names = []
    while len(names) < count:
        name = ask_name(f"Name of {label} {len(names) + 1}: ")
        if name in names:
            print(f"That {label} name was already used. Please enter a unique name.")
            continue
        names.append(name)
    return names


def ask_measurement(group: str, treatment: str, index: int) -> float:
    while True:
        value = input(
            f"  Measurement {index} for {group} / {treatment}: "
        ).strip()
        try:
            measurement = float(value)
        except ValueError:
            print("Please enter a valid number.")
            continue
        if not math.isfinite(measurement):
            print("Please enter a finite number.")
            continue
        return measurement


def analyze(data: list[dict[str, str | float]]) -> list[tuple[str, float, float, float]]:
    model = smf.ols(
        "Measurement ~ C(Group) * C(Treatment)",
        data=pd.DataFrame(data),
    ).fit()
    if model.df_resid <= 0:
        raise ValueError(
            "There are not enough measurements to estimate the residual "
            "variation. Enter additional independent replicates."
        )
    if not math.isfinite(model.mse_resid) or model.mse_resid <= 0:
        raise ValueError(
            "The measurements have no residual variation, so the ANOVA "
            "F-tests and p-values cannot be calculated."
        )

    results = sm.stats.anova_lm(model, typ=2)
    residual_sum_squares = results.loc["Residual", "sum_sq"]
    effects = []
    for source, label in (
        ("C(Group)", "Group"),
        ("C(Treatment)", "Treatment"),
        ("C(Group):C(Treatment)", "Group x Treatment"),
    ):
        effect_sum_squares = results.loc[source, "sum_sq"]
        partial_eta_squared = effect_sum_squares / (
            effect_sum_squares + residual_sum_squares
        )
        effects.append(
            (
                label,
                float(results.loc[source, "F"]),
                float(results.loc[source, "PR(>F)"]),
                float(partial_eta_squared),
            )
        )
    return effects


def main() -> None:
    print("Two-way ANOVA for independent measurements")
    print("Enter each independent replicate for every group-treatment pair.\n")

    group_count = ask_count("Number of groups (at least 2): ", 2)
    groups = ask_names("group", group_count)
    treatment_count = ask_count("Number of treatments (at least 2): ", 2)
    treatments = ask_names("treatment", treatment_count)

    data = []
    for group in groups:
        for treatment in treatments:
            print(f"\n{group} / {treatment}")
            replicate_count = ask_count("  Number of replicates: ")
            for index in range(1, replicate_count + 1):
                data.append(
                    {
                        "Group": group,
                        "Treatment": treatment,
                        "Measurement": ask_measurement(group, treatment, index),
                    }
                )

    try:
        effects = analyze(data)
    except ValueError as error:
        print(error)
        return

    print("\nTwo-way ANOVA results (Type II sums of squares)")
    print(
        f"{'Source':<24} {'F statistic':>12} {'p-value':>12} "
        f"{'Partial eta-squared':>20}"
    )
    print("-" * 72)
    for label, f_statistic, p_value, partial_eta_squared in effects:
        print(
            f"{label:<24} {f_statistic:>12.6g} {p_value:>12.6g} "
            f"{partial_eta_squared:>20.6g}"
        )

    print(
        "\nA small p-value (commonly < 0.05) is evidence of an effect; "
        "partial eta-squared summarizes effect size."
    )
    print(
        "Interpret the group and treatment effects cautiously if the "
        "interaction is significant."
    )


if __name__ == "__main__":
    main()

"""Tkinter desktop interface for the two-way ANOVA program."""

import math
import re
import zipfile
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import pandas as pd
from openpyxl.utils.exceptions import InvalidFileException
from two_way_anova import analyze


def load_excel_data(path: str) -> list[dict[str, str | float]]:
    try:
        frame = pd.read_excel(
            path, sheet_name=0, engine="openpyxl", header=None
        )
    except (
        ImportError,
        InvalidFileException,
        OSError,
        ValueError,
        zipfile.BadZipFile,
    ) as error:
        raise ValueError(f"Could not read the Excel file: {error}") from error

    aliases = {
        "group": {"group", "groups", "groupname", "groupsname"},
        "treatment": {
            "treatment",
            "treatments",
            "treatmentname",
            "treatmentsname",
            "condition",
            "conditions",
        },
    }

    def normalize(value: object) -> str:
        return re.sub(r"[^a-z0-9]", "", str(value).casefold())

    header_row = None
    header_names: list[str] = []
    group_column = treatment_column = None
    for row_index in range(min(len(frame), 10)):
        names = [normalize(value) for value in frame.iloc[row_index]]
        group_matches = [
            index
            for index, name in enumerate(names)
            if name in aliases["group"]
        ]
        treatment_matches = [
            index
            for index, name in enumerate(names)
            if name in aliases["treatment"]
        ]
        if group_matches and treatment_matches:
            header_row = row_index
            header_names = names
            group_column = group_matches[0]
            treatment_column = treatment_matches[0]
            break

    if header_row is None:
        detected_rows = [
            " | ".join(
                str(value).strip()
                for value in frame.iloc[index]
                if not pd.isna(value)
            )
            for index in range(min(len(frame), 10))
        ]
        detected = "; ".join(row for row in detected_rows if row) or "(empty sheet)"
        raise ValueError(
            "Could not find Group and Treatment headers in the first 10 rows "
            "of the first worksheet. Accepted names include Group/Groups and "
            "Treatment/Treatments. Headers found: "
            f"{detected}"
        )

    measurement_columns = [
        index
        for index, name in enumerate(header_names)
        if re.fullmatch(r"(measurement|replicate)\d+", name)
        or name in {"measurement", "replicate", "value"}
    ]
    if not measurement_columns:
        raise ValueError(
            "Add measurement columns named Measurement 1, Measurement 2, "
            "and so on (Replicate 1, Replicate 2 also work)."
        )
    if len(measurement_columns) != len(set(header_names[index] for index in measurement_columns)):
        raise ValueError("The Excel file has duplicate measurement column names.")

    data: list[dict[str, str | float]] = []
    row_combinations: set[tuple[str, str]] = set()
    for row_number, (_, row) in enumerate(
        frame.iloc[header_row + 1 :].iterrows(), start=header_row + 2
    ):
        group = row.iloc[group_column]
        treatment = row.iloc[treatment_column]
        raw_measurements = [row.iloc[column] for column in measurement_columns]
        if pd.isna(group) and pd.isna(treatment) and all(
            pd.isna(value) for value in raw_measurements
        ):
            continue
        if pd.isna(group) or pd.isna(treatment):
            raise ValueError(
                f"Row {row_number} has a blank group or treatment name."
            )

        group_name = str(group).strip()
        treatment_name = str(treatment).strip()
        if not group_name or not treatment_name:
            raise ValueError(
                f"Row {row_number} has a blank group or treatment name."
            )
        combination = (group_name, treatment_name)
        if combination in row_combinations:
            raise ValueError(
                f"Row {row_number} repeats {group_name} / {treatment_name}. "
                "Put replicates in separate Measurement columns on one row."
            )
        row_combinations.add(combination)

        row_measurements = []
        for column_index, raw_measurement in zip(
            measurement_columns, raw_measurements
        ):
            if pd.isna(raw_measurement):
                continue
            column_name = str(frame.iloc[header_row, column_index]).strip()
            try:
                measurement = float(raw_measurement)
            except (TypeError, ValueError) as error:
                raise ValueError(
                    f"{column_name} in row {row_number} must be a number or blank."
                ) from error
            if not math.isfinite(measurement):
                raise ValueError(
                    f"{column_name} in row {row_number} must be a finite number."
                )
            row_measurements.append(measurement)
        if not row_measurements:
            raise ValueError(
                f"Row {row_number} needs at least one measurement."
            )
        for measurement in row_measurements:
            data.append(
                {
                    "Group": group_name,
                    "Treatment": treatment_name,
                    "Measurement": measurement,
                }
            )

    if not data:
        raise ValueError("The first worksheet has no measurement rows.")

    groups = {str(row["Group"]) for row in data}
    treatments = {str(row["Treatment"]) for row in data}
    if len(groups) < 2 or len(treatments) < 2:
        raise ValueError(
            "The file must contain at least two groups and two treatments."
        )
    observed = row_combinations
    missing_combinations = [
        (group, treatment)
        for group in sorted(groups)
        for treatment in sorted(treatments)
        if (group, treatment) not in observed
    ]
    if missing_combinations:
        missing_labels = ", ".join(
            f"{group} / {treatment}"
            for group, treatment in missing_combinations
        )
        raise ValueError(
            "Every group must have measurements for every treatment. "
            f"Missing: {missing_labels}."
        )
    return data


class AnovaApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Two-way ANOVA")
        self.root.geometry("900x900")
        self.root.minsize(720, 640)
        self.excel_path = tk.StringVar()
        self.measurement_fields: list[
            tuple[str, str, ttk.Entry]
        ] = []

        container = ttk.Frame(root, padding=18)
        container.pack(fill="both", expand=True)
        container.columnconfigure(0, weight=1)
        container.rowconfigure(4, weight=1)

        ttk.Label(
            container,
            text="Two-way ANOVA",
            font=("Segoe UI", 20, "bold"),
        ).grid(row=0, column=0, sticky="w")
        ttk.Label(
            container,
            text=(
                "Enter factor names, create a field for each combination, "
                "and enter independent measurements separated by commas."
            ),
            wraplength=820,
        ).grid(row=1, column=0, sticky="w", pady=(4, 16))

        excel = ttk.LabelFrame(container, text="Use an Excel file", padding=10)
        excel.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        excel.columnconfigure(0, weight=1)
        ttk.Label(
            excel,
            text=(
                "Use the first worksheet. Make one row per group-treatment "
                "combination. Headers can say Group or Groups, Treatment or "
                "Treatments, and Measurement 1, Measurement 2, etc. Put "
                "replicates across the row; leave unused measurement cells "
                "blank. Headers may be in the first 10 rows."
            ),
            wraplength=800,
            justify="left",
        ).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 8))
        ttk.Button(
            excel, text="Choose .xlsx file...", command=self.choose_excel_file
        ).grid(row=1, column=0, sticky="w")
        ttk.Label(
            excel,
            textvariable=self.excel_path,
            wraplength=540,
        ).grid(row=1, column=1, sticky="ew", padx=8)
        ttk.Button(
            excel,
            text="Analyze Excel file",
            command=self.run_excel_anova,
        ).grid(row=1, column=2, sticky="e")
        ttk.Label(
            excel,
            text=(
                "Each combination needs at least one measurement. "
                "The first worksheet is analyzed."
            ),
            foreground="#555555",
        ).grid(row=2, column=0, columnspan=3, sticky="w", pady=(6, 0))

        setup = ttk.LabelFrame(container, text="Or enter data manually", padding=12)
        setup.grid(row=3, column=0, sticky="ew", pady=(0, 12))
        setup.columnconfigure(1, weight=1)
        setup.columnconfigure(3, weight=1)
        ttk.Label(setup, text="Groups").grid(row=0, column=0, sticky="w")
        self.groups_entry = ttk.Entry(setup)
        self.groups_entry.grid(row=0, column=1, sticky="ew", padx=(8, 16))
        ttk.Label(setup, text="Treatments").grid(row=0, column=2, sticky="w")
        self.treatments_entry = ttk.Entry(setup)
        self.treatments_entry.grid(row=0, column=3, sticky="ew", padx=(8, 16))
        ttk.Button(
            setup,
            text="Create measurement fields",
            command=self.create_measurement_fields,
        ).grid(row=0, column=4, sticky="ew")
        ttk.Label(
            setup,
            text="Separate names with commas, e.g. Control, Knockout",
            foreground="#555555",
        ).grid(row=1, column=0, columnspan=5, sticky="w", pady=(8, 0))

        measurements = ttk.LabelFrame(
            container, text="Measurements (one or more per combination)", padding=8
        )
        measurements.grid(row=4, column=0, sticky="nsew", pady=(0, 12))
        measurements.columnconfigure(0, weight=1)
        measurements.rowconfigure(0, weight=1)

        self.canvas = tk.Canvas(measurements, highlightthickness=0)
        scrollbar = ttk.Scrollbar(
            measurements, orient="vertical", command=self.canvas.yview
        )
        self.fields_frame = ttk.Frame(self.canvas)
        self.fields_window = self.canvas.create_window(
            (0, 0), window=self.fields_frame, anchor="nw"
        )
        self.fields_frame.bind(
            "<Configure>",
            lambda _event: self.canvas.configure(
                scrollregion=self.canvas.bbox("all")
            ),
        )
        self.canvas.bind(
            "<Configure>",
            lambda event: self.canvas.itemconfigure(
                self.fields_window, width=event.width
            ),
        )
        self.canvas.configure(yscrollcommand=scrollbar.set)
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.canvas.bind_all("<MouseWheel>", self._scroll_measurements)

        results = ttk.LabelFrame(container, text="ANOVA results", padding=10)
        results.grid(row=5, column=0, sticky="ew")
        results.columnconfigure(0, weight=1)
        self.results = ttk.Treeview(
            results,
            columns=("effect", "f", "p", "eta"),
            show="headings",
            height=3,
        )
        self.results.heading("effect", text="Effect")
        self.results.heading("f", text="F statistic")
        self.results.heading("p", text="p-value")
        self.results.heading("eta", text="Partial eta-squared")
        self.results.column("effect", width=200, anchor="w")
        for column in ("f", "p", "eta"):
            self.results.column(column, width=160, anchor="center")
        self.results.grid(row=0, column=0, sticky="ew")
        ttk.Button(
            results, text="Run ANOVA", command=self.run_anova
        ).grid(row=1, column=0, sticky="e", pady=(10, 0))

        explanation = ttk.LabelFrame(
            container, text="What these results mean", padding=10
        )
        explanation.grid(row=6, column=0, sticky="ew", pady=(10, 0))
        ttk.Label(
            explanation,
            text=(
                "ANOVA (analysis of variance) compares average measurements "
                "to test whether groups, treatments, or their interaction "
                "are associated with differences. It assumes independent "
                "observations, approximately normal residuals, and similar "
                "variance across combinations. A significant interaction "
                "means the treatment effect differs by group, so interpret "
                "main effects cautiously. Partial eta-squared is an ANOVA "
                "effect size."
            ),
            wraplength=820,
            justify="left",
        ).grid(row=0, column=0, sticky="w")

    def choose_excel_file(self) -> None:
        path = filedialog.askopenfilename(
            parent=self.root,
            title="Choose an Excel workbook",
            filetypes=[("Excel workbook", "*.xlsx")],
        )
        if path:
            self.excel_path.set(path)

    def run_excel_anova(self) -> None:
        path = self.excel_path.get()
        if not path:
            messagebox.showerror(
                "Choose an Excel file",
                "Click 'Choose .xlsx file...' and select your workbook first.",
                parent=self.root,
            )
            return
        try:
            effects = analyze(load_excel_data(path))
        except ValueError as error:
            messagebox.showerror("Could not run ANOVA", str(error), parent=self.root)
            return

        self._show_results(effects)

    def _scroll_measurements(self, event: tk.Event) -> None:
        self.canvas.yview_scroll(int(-event.delta / 120), "units")

    @staticmethod
    def _parse_names(value: str, factor: str) -> list[str]:
        names = [name.strip() for name in value.split(",") if name.strip()]
        if len(names) < 2:
            raise ValueError(f"Enter at least two {factor} names.")
        if len(set(names)) != len(names):
            raise ValueError(f"{factor.capitalize()} names must be unique.")
        return names

    def create_measurement_fields(self) -> None:
        try:
            groups = self._parse_names(self.groups_entry.get(), "group")
            treatments = self._parse_names(
                self.treatments_entry.get(), "treatment"
            )
        except ValueError as error:
            messagebox.showerror("Check factor names", str(error), parent=self.root)
            return

        for child in self.fields_frame.winfo_children():
            child.destroy()
        self.measurement_fields.clear()
        for row, (group, treatment) in enumerate(
            (group, treatment)
            for group in groups
            for treatment in treatments
        ):
            ttk.Label(
                self.fields_frame,
                text=f"{group} / {treatment}",
                width=28,
            ).grid(row=row, column=0, sticky="w", padx=(4, 12), pady=5)
            entry = ttk.Entry(self.fields_frame)
            entry.grid(row=row, column=1, sticky="ew", padx=4, pady=5)
            self.fields_frame.columnconfigure(1, weight=1)
            self.measurement_fields.append((group, treatment, entry))
        self.results.delete(*self.results.get_children())
        self.canvas.yview_moveto(0)

    def run_anova(self) -> None:
        if not self.measurement_fields:
            messagebox.showerror(
                "No measurement fields",
                "Enter factor names and create the measurement fields first.",
                parent=self.root,
            )
            return

        data: list[dict[str, str | float]] = []
        try:
            for group, treatment, entry in self.measurement_fields:
                raw_values = entry.get().replace("\n", ",").split(",")
                values = [value.strip() for value in raw_values if value.strip()]
                if not values:
                    raise ValueError(
                        f"Enter at least one measurement for "
                        f"{group} / {treatment}."
                    )
                for value in values:
                    try:
                        measurement = float(value)
                    except ValueError as error:
                        raise ValueError(
                            f"'{value}' is not a valid number for "
                            f"{group} / {treatment}."
                        ) from error
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
        except ValueError as error:
            messagebox.showerror("Could not run ANOVA", str(error), parent=self.root)
            return

        self._show_results(effects)

    def _show_results(
        self, effects: list[tuple[str, float, float, float]]
    ) -> None:
        self.results.delete(*self.results.get_children())
        for label, f_statistic, p_value, eta_squared in effects:
            self.results.insert(
                "",
                "end",
                values=(
                    label,
                    f"{f_statistic:.6g}",
                    f"{p_value:.6g}",
                    f"{eta_squared:.6g}",
                ),
            )


def main() -> None:
    root = tk.Tk()
    AnovaApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()

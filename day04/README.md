# Two-way ANOVA

This interactive program tests independent measurements for effects of two factors: group, treatment, and their interaction. It reports an F statistic, p-value, and partial eta-squared effect size for each effect. Partial eta-squared estimates the share of effect-plus-error variation associated
with that ANOVA effect.

## Day 4 overview

Day 4 was about turning the two-way ANOVA idea into something easier to use in real life. I started with a simple Python program that could read group names, treatment names, and measurements, then calculate the ANOVA results and p-values for the main effects and interaction.

I then asked Copilot to improve it into a desktop-style GUI so it would open in a separate window, and later to add an explanation of ANOVA directly into the interface. I also asked for clearer installation steps for someone who is not familiar with Python or terminal commands. Finally, I added Excel upload support so the tool could read biological data from a spreadsheet with separate measurement columns instead of one long list of rows.

### Prompts used with Copilot

- "Write me a Python program that can perform ANOVA on data from biological experiments. The program should have a clear interface where the names of the groups and treatments are entered, along with the measurements, and it should produce the ANOVA results and p-values."
- "Make this program open in a nice separate window. Does it need to be changed to HTML for that?"
- "Add the ANOVA explanation paragraph into the GUI itself, and make the installation instructions much simpler and clearer for someone with no background in this."
- "Add an option to upload an Excel file with instructions on how to structure it. I also want the measurements in separate columns rather than rows."
- "Write some tests for the "business logic" of your previous applications. You can put them in your day04."
- "ok but we need to independantely verify the calculation. if you need an external data set let me know"

This is what I built: a working two-way ANOVA tool with a simple interface, a desktop GUI, a web version, and an Excel import feature that reads biological replicate data in a clear tabular format.

## Run the web application

This Flask interface uses the same ANOVA calculation as the command-line and
desktop programs. From the repository folder, install the requirements:

```powershell
py -m pip install -r .\day04\requirements.txt
```

Start the web app:

```powershell
py .\day04\app.py
```

Open <http://127.0.0.1:5000> in your browser. Enter at least two unique group
names and treatment names, then enter one or more comma-separated measurements
for every combination. Press **Run ANOVA** to view the results. Press
**Ctrl+C** in the terminal to stop the server.

## Open the desktop window (Windows)

1. Open this project in VS Code.
2. Select **Terminal** → **New Terminal** from the top menu.
3. Copy this line into the terminal and press **Enter**. This installs the program's required packages. You only need to do this once:

   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r .\day04\requirements.txt
   ```

4. After the installation finishes, copy this line into the terminal and
   press **Enter** to open the program:

   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" .\day04\two_way_anova_gui.py
   ```

Next time, open a new VS Code terminal and run only step 4. If Python 3.12 isn't installed in the location above, ask for help setting up Python before running these commands.

The original terminal interface is still available by replacing
`two_way_anova_gui.py` in step 4 with `two_way_anova.py`.

ANOVA compares average measurements to test whether group, treatment, or their
interaction is associated with differences. It assumes independent
observations, approximately normal residuals, and similar variance across
combinations. A significant interaction means the treatment effect differs by
group, so interpret main effects cautiously. Partial eta-squared is an ANOVA
effect size. This program is for independent observations, not repeated
measurements on the same subjects.

## Import measurements from Excel

The GUI can analyze an `.xlsx` workbook directly. In the first worksheet,
make **one row for each group-treatment combination**. Put replicate
measurements in separate columns, so you only enter the group and treatment
names once per combination:

| Group | Treatment | Measurement 1 | Measurement 2 | Measurement 3 |
|---|---|---:|---:|---:|
| Control | Vehicle | 1.2 | 1.5 | |
| Control | Drug | 2.1 | 2.4 | |
| Knockout | Vehicle | 2.0 | 2.3 | |
| Knockout | Drug | 3.1 |  | |

Use the column headers `Group` (or `Groups`), `Treatment` (or `Treatments`),
and `Measurement 1`, `Measurement 2`, etc. `Replicate 1`, `Replicate 2`, etc.
also work. Leave unused measurement cells blank if some combinations have
fewer replicates. Each row needs at least one measurement. Include at least
two groups and two treatments, and one row for every group-treatment
combination. Do not repeat a group-treatment combination on multiple rows.
Extra columns are okay. The headers can be within the first 10 rows; the GUI
reads only the first worksheet.

In the GUI, click **Choose .xlsx file...**, select your workbook, then click
**Analyze Excel file**. If you already installed the program, run the
dependency-install command from step 3 above once more to install the Excel
reader.

## Run the copied command-line version

```powershell
py .\day04\two_way_anova.py
```

## Run the tests

```powershell
Push-Location .\day04
py -m unittest discover -s .\tests
Pop-Location
```

The tests cover the ANOVA calculation and the web interface. The business-logic
test compares the program's output with values calculated separately for the
small balanced dataset below; it does not use the program to generate its
expected answers.

| Group | Treatment | Measurements | Cell mean |
|---|---|---:|---:|
| G1 | T1 | 1, 2 | 1.5 |
| G1 | T2 | 3, 4 | 3.5 |
| G2 | T1 | 5, 6 | 5.5 |
| G2 | T2 | 9, 10 | 9.5 |

The grand mean is 5. The group means are 2.5 and 7.5, and the treatment means
are 3.5 and 6.5. There are two measurements in each cell. Using the standard
balanced two-way ANOVA sums-of-squares formulas:

- Group: `2 treatments * 2 measurements * ((2.5 - 5)^2 + (7.5 - 5)^2) = 50`.
- Treatment: `2 groups * 2 measurements * ((3.5 - 5)^2 + (6.5 - 5)^2) = 18`.
- Interaction: each cell's interaction deviation is
  `cell mean - group mean - treatment mean + grand mean`, giving `0.5, -0.5,
  -0.5, 0.5`. Thus `2 measurements * sum(deviation^2) = 2`.
- Error: each cell has two observations half a unit from its cell mean, so
  `4 cells * ((-0.5)^2 + 0.5^2) = 2`.

The error degrees of freedom are `2 groups * 2 treatments * (2 measurements -
1) = 4`, so the mean squared error is `2 / 4 = 0.5`. Each effect has one
degree of freedom, so `F = effect sum of squares / 0.5`. The expected results
are:

| Effect | F statistic | p-value (F distribution, 1 and 4 df) | Partial eta-squared |
|---|---:|---:|---:|
| Group | 100 | 0.0005620 | `50 / (50 + 2)` = 0.961538 |
| Treatment | 36 | 0.0038825 | `18 / (18 + 2)` = 0.9 |
| Group x Treatment | 4 | 0.1161165 | `2 / (2 + 2)` = 0.5 |

The test calculates the F(1, 4) upper-tail p-value with the closed-form
expression `1 - 1.5*sqrt(F/(F+4)) + 0.5*(F/(F+4))^(3/2)`. Partial eta-squared
is calculated as `effect sum of squares / (effect sum of squares + error sum
of squares)`. These reference calculations are independent of the application's
Statsmodels ANOVA output.

A separate business-logic test verifies that data with only one observation
per group-treatment cell is rejected because there are no residual degrees of
freedom to estimate error. The web tests check that the form loads, valid data
displays results, missing measurements are reported, and duplicate factor
names are rejected.

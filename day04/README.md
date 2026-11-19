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

# Day 5: Tests

Day 5 was about checking that the application works without manually trying every
case by hand. The test work belongs to Day 5, even though the test files are
currently kept inside the Day 4 application's `day04/tests` folder.

## What is inside the test folder?

The `day04/tests` folder contains two Python test files:

| File | What it checks |
|---|---|
| `test_app.py` | Checks the web page and web form. |
| `test_two_way_anova.py` | Checks the ANOVA calculation and its error handling. |

Each test is a small example of something the program should do. A passing test
means the program behaved as expected for that example.

## Step 1: Start from the project folder

The tests use Python's built-in test runner, so no extra test package is needed.
Open a terminal in the repository folder. The repository folder is the folder
that contains `day01`, `day02`, `day03`, and `day04`.

From that folder, run:

```powershell
Push-Location .\day04
py -m unittest discover -s .\tests
Pop-Location
```

These commands mean:

1. `Push-Location .\day04` enters the Day 4 project folder.
2. `py -m unittest discover -s .\tests` finds files named `test*.py` and runs
   every test in the `tests` folder.
3. `Pop-Location` returns to the original repository folder.

The most important result is the final line:

```text
OK
```

This means all discovered tests passed.

## Step 2: What `test_app.py` checks

`test_app.py` uses a test client to send requests to the Flask application. It
does not need a real browser.

It checks four things:

1. The home page opens successfully.
2. The page contains the group and treatment fields and the "Run ANOVA" button.
3. Valid measurements produce an ANOVA results table.
4. Missing measurements, and repeated factor names, show helpful error messages.

These tests check the web interface and form behavior. They do not calculate the
expected ANOVA numbers by themselves.

## Step 3: What `test_two_way_anova.py` checks

`test_two_way_anova.py` checks the shared ANOVA business logic. It contains two
tests:

1. It compares the application result with calculations worked out separately.
2. It checks that incomplete data is rejected when there are no residual degrees
   of freedom.

The second test uses only one observation for each group-treatment cell. Because
the program cannot estimate leftover error variation from that data, it returns
a clear `ValueError` instead of an unreliable ANOVA result.

## Step 4: Independently checking the calculation

The calculation test uses a small, balanced example that can be checked by hand.
No external dataset is required.

| Group | Treatment | Measurements | Cell mean |
|---|---|---:|---:|
| G1 | T1 | 1, 2 | 1.5 |
| G1 | T2 | 3, 4 | 3.5 |
| G2 | T1 | 5, 6 | 5.5 |
| G2 | T2 | 9, 10 | 9.5 |

The overall mean is 5.

- The group means are 2.5 and 7.5.
- The treatment means are 3.5 and 6.5.
- There are two measurements in every cell.

### Group sum of squares

The difference of each group mean from the overall mean is squared and weighted
by the number of measurements in that group:

```text
2 treatments * 2 measurements * ((2.5 - 5)^2 + (7.5 - 5)^2)
= 50
```

### Treatment sum of squares

The difference of each treatment mean from the overall mean is squared and
weighted by the number of measurements in that treatment:

```text
2 groups * 2 measurements * ((3.5 - 5)^2 + (6.5 - 5)^2)
= 18
```

### Interaction sum of squares

First, find the interaction deviation for each cell:

```text
cell mean - group mean - treatment mean + overall mean
```

The four deviations are `0.5`, `-0.5`, `-0.5`, and `0.5`. Each deviation is
squared and weighted by the two measurements in its cell:

```text
2 measurements * (0.5^2 + (-0.5)^2 + (-0.5)^2 + 0.5^2)
= 2
```

### Error sum of squares

Within each cell, both observations are 0.5 away from the cell mean. Thus:

```text
4 cells * ((-0.5)^2 + 0.5^2)
= 2
```

### F statistics

There are four error degrees of freedom:

```text
2 groups * 2 treatments * (2 measurements - 1) = 4
```

The mean squared error is:

```text
2 error sum of squares / 4 error degrees of freedom = 0.5
```

Each effect has one degree of freedom, so the F statistic is:

```text
effect sum of squares / 0.5
```

| Effect | Effect sum of squares | F statistic | p-value | Partial eta-squared |
|---|---:|---:|---:|---:|
| Group | 50 | 100 | 0.0005620 | `50 / (50 + 2)` = 0.961538 |
| Treatment | 18 | 36 | 0.0038825 | `18 / (18 + 2)` = 0.9 |
| Group x Treatment | 2 | 4 | 0.1161165 | `2 / (2 + 2)` = 0.5 |

The p-values above are for an F distribution with 1 and 4 degrees of freedom.
The test calculates them using this independent closed-form expression:

```text
1 - 1.5 * sqrt(F / (F + 4)) + 0.5 * (F / (F + 4))^(3/2)
```

Partial eta-squared is the effect sum of squares divided by the effect sum of
squares plus the error sum of squares.

These reference values were calculated independently of the Statsmodels output
used inside the application. This makes the test useful: if the application
calculation changes incorrectly, the test can catch the difference.

## Prompts used for the testing work

- "Write some tests for the "business logic" of your previous applications. You can put them in your day04."
- "ok but we need to independantely verify the calculation. if you need an external data set let me know"
- "include in the read me in a simple explanation the tests and calculations, if you performed calculations also write them out, and add the prompts i used"
- "seperate it in a way that explains that the tests belong to day 05 and also what exactly is inside the test folder. really go step by step and simply for people with no coing background"

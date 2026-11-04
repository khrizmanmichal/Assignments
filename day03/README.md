# Two-way ANOVA

This interactive program tests independent measurements for effects of two factors: group, treatment, and their interaction. It reports an F statistic, p-value, and partial eta-squared effect size for each effect. Partial eta-squared estimates the share of effect-plus-error variation associated
with that ANOVA effect.

Prompts used with Copilot: write me a python program that can perfrom anova on data from biological expreiments. The program should have a clear interface where the names of the groups and treatments are inserted as well as the measurements, and produce not only the anova but also the p value.
Later, I asked it to have a nice gui: i want this program to open nicely in a sepereate window does it need to be changed to html for that?
next prompt: two changes: I want you to add the final paragraph of the readme into the gui itself (that explain what anova is). i also want you to make the instructions of the gui installation much simpler and clearer for a person who has no background with these things
final prompt:add to the gui an option to upload an excel file with instructions on how to structure it. I also asked it to have seperate measurements in different columns, not rows.

## Open the desktop window (Windows)

1. Open this project in VS Code.
2. Select **Terminal** → **New Terminal** from the top menu.
3. Copy this line into the terminal and press **Enter**. This installs the program's required packages. You only need to do this once:

   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" -m pip install -r .\day03\requirements.txt
   ```

4. After the installation finishes, copy this line into the terminal and
   press **Enter** to open the program:

   ```powershell
   & "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe" .\day03\two_way_anova_gui.py
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

# Project Guide: Student Performance Analytics & Early Warning System

## 1. What the project does

This project turns a small student CSV into a readable class snapshot. It combines four subject marks with attendance, calculates academic summaries, identifies students who may benefit from support, prints a terminal dashboard, exports an enriched CSV, and generates a static browser dashboard. The supplied records are fictional and intended only for demonstration; the current sample roster contains 30 students.

This is a simple decision-support example, not a diagnosis or an automatic decision about a student's ability. An alert should start a supportive conversation and be checked against context such as illness, data-entry mistakes, or access to learning resources.

## 2. Tools and concepts

- **Python** structures the program into functions, uses conditions and loops, handles errors, and controls the run sequence.
- **Pandas** reads CSV files into tables, calculates row/column values, sorts records, and writes the final report.
- **NumPy** calculates each student's average using an array of subject marks.
- **CSV** is plain-text tabular data that can be viewed in a spreadsheet application.

## 3. Folder tour

- `main.py`: source code.
- `data/students.csv`: fictional input data.
- `reports/`: generated output reports are placed here; reports are ignored by Git by default.
- `tests/test_main.py`: small automated tests.
- `requirements.txt`: NumPy and Pandas dependency list.
- `README.md`: quick start and GitHub setup.

## 4. Set up and run

Use Python 3.10 or later. Open a terminal at the project root and run:

```text
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

On Windows, activate the environment with `.venv\\Scripts\\activate` instead of the `source` command. Run checks with `python -m unittest discover -s tests -v`. The program creates the `reports` directory when saving the output file.

To select another file, use `python main.py --input path/to/class.csv --output path/to/report.csv`. The input must contain `student_id`, `name`, `class`, `attendance_pct`, and one column for each subject listed in `SUBJECTS`. Marks and attendance must be numbers from 0 to 100.

## 5. How the code works, step by step

### Step 1: Rules and file paths

At the top of `main.py`, constants store the pass mark, attendance threshold, low-average threshold, subject names, and default file paths. Keeping these settings in one place makes the project easy to adapt.

### Step 2: Read and validate the CSV

`load_student_data()` checks that the file exists, reads it with Pandas, confirms required column names, and checks that every mark/attendance entry is numeric and between 0 and 100. Validation gives a clear error rather than allowing bad data to silently affect results.

### Step 3: Calculate the grade

`calculate_grade()` uses a sequence of `if` conditions to map an average to a letter grade. The boundaries are examples for this project and should be aligned with the instructor's preferred grading policy when presenting it.

### Step 4: Add analysis columns

`analyze_students()` makes a copy of the input table so the raw data is not changed. It uses Pandas to calculate total marks, NumPy to calculate average marks, and `apply()` to call the grade function for each student. `np.where()` applies a pass/fail condition: all subject scores must meet the pass mark.

`idxmin(axis=1)` finds the subject with the lowest score for each row. A small helper builds an alert from three transparent rules: any failing subject, attendance below the configured limit, or an overall average below the configured limit. Another helper chooses a study suggestion from the weakest subject and alert conditions.

### Step 5: Print the dashboard

`print_dashboard()` calculates class-level counts and averages. A loop prints each subject average with a simple text bar. The table is sorted by average to display up to five passing students. A second loop presents alerts and corresponding suggestions. The summary table shows a compact record per student.

### Step 6: Export the report

`save_report()` creates the output folder if it does not exist and writes all original and calculated columns to CSV. Open the file in a spreadsheet application to inspect or filter the results. `save_html_dashboard()` writes a self-contained static HTML page with summary cards, attendance bands, subject and lecturer cards, student account profiles, alerts, campus invitations, study prompts, and marks records. Profile details use the browser's built-in expandable disclosure element; there is no JavaScript, framework, or server. Python generates the report, and NumPy/Pandas perform the calculations. Plain HTML/CSS are only the browser's page structure and styling. Open `reports/student_dashboard.html` in a browser to view it. Lecturer names, term details, and events in the demo are fictional sample content; replace them with authorized institutional information before adapting the presentation.

### Step 7: Connect the workflow

`main()` reads optional command-line input/output paths, runs the functions in order, and reports common input errors through `argparse`. The `if __name__ == "__main__"` guard means importing functions for tests does not automatically run the dashboard.

## 6. Data columns

| Column | Meaning |
| --- | --- |
| `student_id` | Demonstration-only student key |
| `name` | Fictional student's display name |
| `class` | Class/group label |
| `attendance_pct` | Attendance percentage from 0 to 100 |
| `Maths`, `Science`, `English`, `Computer` | Subject marks from 0 to 100 |

The report adds `total_marks`, `average`, `grade`, `result`, `weakest_subject`, `early_warning`, and `study_suggestion`.

## 7. Customize it safely

1. Edit the fictional values in `data/students.csv`; preserve the header names and valid numeric range.
2. Adjust `PASS_MARK`, `LOW_ATTENDANCE_LIMIT`, or `LOW_AVERAGE_LIMIT` near the top of `main.py` to match a clearly stated class policy.
3. To add or rename a subject, update `SUBJECTS` and ensure the CSV has a matching column. The total and average calculations will include the new subject automatically.
4. Change grade ranges only in `calculate_grade()` and explain the scheme in your presentation.
5. Improve suggestions by adding a condition to `create_study_suggestion()`. Keep them constructive, specific, and non-punitive.
6. Run the tests and rerun `python main.py` to inspect the new dashboard and report.

## 8. Suggested mini-project presentation

1. **Problem:** reviewing marks and attendance manually can make patterns harder to spot.
2. **Aim:** summarize records and offer early, supportive follow-up indicators.
3. **Input:** show the CSV columns and explain that demo records are fictional.
4. **Logic:** explain pass/fail, grade bands, attendance threshold, weakest subject, and alert rules.
5. **Demonstration:** run the program, point out class averages/top performers/alerts, then open the generated report.
6. **Testing:** run the unit tests and show how they cover grade boundaries, a failed subject, and input data.
7. **Limitations and future work:** thresholds are configurable examples; a single score cannot explain a student's circumstances. A real deployment would require consent, data protection, careful validation, and human review.

## 9. Viva practice questions

**Why use Pandas?** It provides convenient CSV reading/writing and tabular calculations.

**Where is NumPy used?** It calculates the mean of each student's subject-mark array.

**How is pass/fail decided?** A student passes only if every subject meets `PASS_MARK`; an average alone cannot hide a failed subject.

**What is an early warning?** A transparent flag generated by configured rules, meant to prompt a human check-in rather than make a decision.

**Why validate input?** Missing columns, non-numeric marks, or out-of-range values can produce misleading results or runtime errors.

**How does the program find the weakest subject?** It identifies the smallest subject value in each student's row using Pandas `idxmin()`.

**What could be improved?** Add configurable subject sets, compare multiple terms, include trend checks, and improve accessibility while protecting student privacy.

**What is a limitation?** The dataset is small and fictional, and the thresholds/suggestions are simple examples rather than validated educational policy.

## 10. GitHub publishing checklist

Create a repository, then from the project root run `git init`, `git add .`, and `git commit -m "Add student performance analytics mini-project"`. Add your GitHub repository as the `origin` remote and push the branch. Review the staged files before publishing. Do not commit real student information or generated reports containing private records. The supplied `.gitignore` excludes virtual environments and generated report CSVs.

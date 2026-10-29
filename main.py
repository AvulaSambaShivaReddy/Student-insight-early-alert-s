"""Student Performance Analytics & Early Warning System.

A beginner-friendly command-line project that reads student data from CSV,
calculates academic indicators, prints a dashboard, and exports a report.
"""

from pathlib import Path
import argparse
from html import escape

import numpy as np
import pandas as pd


# Change these values to customize the project rules.
PASS_MARK = 40
LOW_ATTENDANCE_LIMIT = 75
LOW_AVERAGE_LIMIT = 50
SUBJECTS = ["Maths", "Science", "English", "Computer"]
DATA_FILE = Path("data/students.csv")
REPORT_FILE = Path("reports/student_performance_report.csv")
HTML_REPORT_FILE = Path("reports/student_dashboard.html")


def load_student_data(csv_path: Path) -> pd.DataFrame:
    """Read and validate the input CSV file."""
    if not csv_path.exists():
        raise FileNotFoundError(f"Dataset not found: {csv_path}")

    students = pd.read_csv(csv_path)
    required_columns = {"student_id", "name", "class", "attendance_pct", *SUBJECTS}
    missing_columns = required_columns.difference(students.columns)
    if missing_columns:
        missing = ", ".join(sorted(missing_columns))
        raise ValueError(f"CSV is missing required columns: {missing}")
    if students.empty:
        raise ValueError("The CSV contains no student records.")

    numeric_columns = ["attendance_pct", *SUBJECTS]
    for column in numeric_columns:
        students[column] = pd.to_numeric(students[column], errors="coerce")
        if students[column].isna().any():
            raise ValueError(f"Column '{column}' must contain valid numbers for every student.")
        if not students[column].between(0, 100).all():
            raise ValueError(f"Values in '{column}' must be between 0 and 100.")

    return students


def calculate_grade(average: float) -> str:
    """Convert a percentage average into a simple letter grade."""
    if average >= 90:
        return "A+"
    if average >= 80:
        return "A"
    if average >= 70:
        return "B"
    if average >= 60:
        return "C"
    if average >= 50:
        return "D"
    if average >= PASS_MARK:
        return "E"
    return "F"


def create_study_suggestion(row: pd.Series) -> str:
    """Return a practical suggestion based on a student's main needs."""
    weak_subject = row[SUBJECTS].astype(float).idxmin()
    weak_mark = float(row[weak_subject])

    if weak_mark < PASS_MARK:
        suggestion = f"Meet the teacher and review {weak_subject} fundamentals"
    elif row["attendance_pct"] < LOW_ATTENDANCE_LIMIT:
        suggestion = "Improve attendance and catch up on missed lessons"
    elif row["average"] < LOW_AVERAGE_LIMIT:
        suggestion = f"Use a weekly revision plan, starting with {weak_subject}"
    else:
        suggestion = f"Maintain the routine and stretch yourself in {weak_subject}"
    return suggestion


def analyze_students(students: pd.DataFrame) -> pd.DataFrame:
    """Add totals, averages, grades, outcomes, alerts, and suggestions."""
    results = students.copy()
    results["total_marks"] = results[SUBJECTS].sum(axis=1)
    # NumPy is used here to calculate averages across the subject mark array.
    results["average"] = np.round(np.mean(results[SUBJECTS].to_numpy(dtype=float), axis=1), 1)
    results["grade"] = results["average"].apply(calculate_grade)
    results["result"] = np.where((results[SUBJECTS] >= PASS_MARK).all(axis=1), "PASS", "FAIL")
    results["weakest_subject"] = results[SUBJECTS].idxmin(axis=1)

    def make_alert(row: pd.Series) -> str:
        alerts = []
        if (row[SUBJECTS] < PASS_MARK).any():
            alerts.append("Subject mark below pass mark")
        if row["attendance_pct"] < LOW_ATTENDANCE_LIMIT:
            alerts.append("Low attendance")
        if row["average"] < LOW_AVERAGE_LIMIT:
            alerts.append("Low overall average")
        return "; ".join(alerts) if alerts else "No alert"

    results["early_warning"] = results.apply(make_alert, axis=1)
    results["study_suggestion"] = results.apply(create_study_suggestion, axis=1)
    return results


def print_dashboard(results: pd.DataFrame) -> None:
    """Print a compact, readable class dashboard."""
    passed = int((results["result"] == "PASS").sum())
    failed = len(results) - passed
    alert_count = int((results["early_warning"] != "No alert").sum())
    class_average = float(results["average"].mean())
    subject_averages = results[SUBJECTS].mean().sort_values(ascending=False)
    eligible = results[results["result"] == "PASS"]

    print("\n" + "=" * 68)
    print("  STUDENT PERFORMANCE ANALYTICS & EARLY WARNING SYSTEM")
    print("=" * 68)
    print(f"Students analyzed : {len(results)}")
    print(f"Class average     : {class_average:.1f}%")
    print(f"Pass / Fail       : {passed} / {failed}")
    print(f"Students alerted  : {alert_count}")
    print("\nSUBJECT AVERAGES")
    for subject, average in subject_averages.items():
        bar = "#" * int(round(average / 5))
        print(f"  {subject:<10} {average:5.1f}%  {bar}")

    print("\nTOP PERFORMERS (passing students, ranked by average)")
    if eligible.empty:
        print("  No students currently meet the pass criteria.")
    else:
        top = eligible.sort_values(["average", "name"], ascending=[False, True]).head(5)
        print(top[["student_id", "name", "average", "grade"]].to_string(index=False))

    print("\nEARLY-WARNING FOLLOW-UP")
    flagged = results[results["early_warning"] != "No alert"]
    if flagged.empty:
        print("  No students currently meet the alert rules.")
    else:
        for _, row in flagged.sort_values("average").iterrows():
            print(f"  {row['name']} ({row['student_id']}) — {row['early_warning']}")
            print(f"    Suggestion: {row['study_suggestion']}")

    print("\nSTUDENT SUMMARY")
    display_columns = ["student_id", "name", "average", "grade", "result", "attendance_pct", "weakest_subject"]
    print(results[display_columns].to_string(index=False))
    print("=" * 68)


def save_report(results: pd.DataFrame, output_path: Path) -> None:
    """Create the report folder (if needed) and save all student indicators."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(output_path, index=False)
    print(f"\nCSV report saved to: {output_path}")


def save_html_dashboard(results: pd.DataFrame, output_path: Path) -> None:
    """Create a standalone, interactive academic dashboard without a server."""
    output_path.parent.mkdir(parents=True, exist_ok=True)
    passed = int((results["result"] == "PASS").sum())
    failed = len(results) - passed
    alert_count = int((results["early_warning"] != "No alert").sum())
    class_average = float(results["average"].mean())
    subject_averages = results[SUBJECTS].mean().sort_values(ascending=False)
    top_students = results[results["result"] == "PASS"].sort_values(
        ["average", "name"], ascending=[False, True]
    ).head(5)
    flagged_students = results[results["early_warning"] != "No alert"].sort_values("average")

    attendance_bands = {
        "On track · 90%+": int((results["attendance_pct"] >= 90).sum()),
        "Steady · 75–89%": int(results["attendance_pct"].between(75, 89.99).sum()),
        "Follow up · below 75%": int((results["attendance_pct"] < LOW_ATTENDANCE_LIMIT).sum()),
    }
    grade_order = ["A+", "A", "B", "C", "D", "E", "F"]
    grade_counts = results["grade"].value_counts().reindex(grade_order, fill_value=0)
    grade_rows = "".join(
        f'<div class="grade-row"><span class="grade-label">{grade}</span>'
        f'<div class="bar-track"><div class="bar grade-bar" '
        f'style="width:{count / len(results) * 100:.1f}%"></div></div>'
        f'<strong>{count}</strong></div>'
        for grade, count in grade_counts.items()
    )
    average_attendance = float(results["attendance_pct"].mean())
    strongest_subject = str(subject_averages.index[0])
    focus_subject = str(subject_averages.index[-1])
    attendance_rows = "".join(
        f'<div class="attendance-row"><span>{escape(label)}</span>'
        f'<div class="bar-track"><div class="bar attendance-bar" '
        f'style="width:{count / len(results) * 100:.1f}%"></div></div>'
        f'<strong>{count} students</strong></div>'
        for label, count in attendance_bands.items()
    )

    lecturers = {
        "Maths": "Ms. Kavita Rao",
        "Science": "Mr. Arjun Nair",
        "English": "Ms. Leena Thomas",
        "Computer": "Mr. Rohan Sen",
    }
    subject_cards = "".join(
        f'<article class="subject-card"><div class="subject-top"><span class="subject-icon">'
        f'{escape(subject[:1])}</span><span class="subject-score">{float(average):.1f}%</span></div>'
        f'<h3>{escape(str(subject))}</h3><p>Lecturer · {escape(lecturers.get(subject, "Class instructor"))}</p>'
        f'<div class="bar-track"><div class="bar" style="width:{float(average):.1f}%"></div></div>'
        f'<small>Class mark average</small></article>'
        for subject, average in subject_averages.items()
    )
    top_rows = "".join(
        f'<tr><td>{escape(str(row["name"]))}</td><td>{float(row["average"]):.1f}%</td>'
        f'<td><span class="grade">{escape(str(row["grade"]))}</span></td></tr>'
        for _, row in top_students.iterrows()
    ) or '<tr><td colspan="3">No passing students yet.</td></tr>'
    alert_cards = "".join(
        f'<article class="alert-card"><div><strong>{escape(str(row["name"]))}</strong>'
        f'<span class="student-id">{escape(str(row["student_id"]))}</span></div>'
        f'<p>{escape(str(row["early_warning"]))}</p>'
        f'<small>Suggested next step: {escape(str(row["study_suggestion"]))}</small></article>'
        for _, row in flagged_students.iterrows()
    ) or '<p class="muted">No students currently meet the alert rules.</p>'

    table_rows = "".join(
        f'<tr>'
        f'<td>{escape(str(row["student_id"]))}</td><td>{escape(str(row["name"]))}</td>'
        f'<td>{float(row["average"]):.1f}%</td><td>{escape(str(row["grade"]))}</td>'
        f'<td><span class="result {str(row["result"]).lower()}">{escape(str(row["result"]))}</span></td>'
        f'<td>{float(row["attendance_pct"]):.0f}%</td>'
        + "".join(f'<td>{float(row[subject]):.0f}%</td>' for subject in SUBJECTS)
        + f'<td>{escape(str(row["weakest_subject"]))}</td></tr>'
        for _, row in results.iterrows()
    )

    profile_cards = "".join(
        f'<details class="student-profile"{" open" if index == 0 else ""}>'
        f'<summary><span class="avatar">{escape(str(row["name"])[:1].upper())}</span>'
        f'<span class="profile-heading"><strong>{escape(str(row["name"]))}</strong>'
        f'<small>{escape(str(row["student_id"]))} · Class {escape(str(row["class"]))}</small></span>'
        f'<span class="profile-quick">Average <strong>{float(row["average"]):.1f}%</strong></span>'
        f'<span class="profile-quick">Attendance <strong>{float(row["attendance_pct"]):.0f}%</strong></span>'
        f'<span class="profile-status {"fail-status" if row["result"] == "FAIL" else ""}">'
        f'{"NEEDS SUPPORT" if row["result"] == "FAIL" else "ON TRACK"}</span></summary>'
        f'<div class="profile-details"><div class="mark-list">'
        + "".join(
            f'<div class="mark-item"><span>{escape(subject)}</span>'
            f'<strong>{float(row[subject]):.0f}%</strong></div>'
            for subject in SUBJECTS
        )
        + f'</div><p class="profile-tip"><strong>Grade {escape(str(row["grade"]))} · '
        f'Focus subject: {escape(str(row["weakest_subject"]))}</strong><br>'
        f'Study nudge: {escape(str(row["study_suggestion"]))}</p></div></details>'
        for index, (_, row) in enumerate(results.iterrows())
    )

    # Fictional campus events and invitations make the demo feel like a student portal.
    events = [
        ("NOV 05", "Mathematics Problem-Solving Lab", "Academic workshop", "Invited · Room 204"),
        ("NOV 12", "Innovation & Coding Fest", "Campus fest", "Invitation · Main auditorium"),
        ("NOV 18", "Science Discovery Showcase", "Student exhibition", "Open invitation · Science block"),
        ("NOV 24", "Peer Study Circle: Exam Reset", "Study session", "Invited · Library study hall"),
    ]
    event_cards = "".join(
        f'<article class="event-card"><div class="event-date">{escape(date)}</div>'
        f'<div class="event-info"><span class="event-type">{escape(kind)}</span>'
        f'<h3>{escape(title)}</h3><p>{escape(invitation)}</p></div>'
        f'<span class="invite-tag">Demo invitation</span></article>'
        for date, title, kind, invitation in events
    )

    study_cards = "".join(
        f'<article class="study-card"><span class="study-number">0{index}</span>'
        f'<h3>{escape(subject)} focus</h3><p>{escape(description)}</p>'
        f'<span class="study-time">{escape(duration)}</span></article>'
        for index, (subject, description, duration) in enumerate([
            ("Maths", "Practice 5 mixed problems, then review the worked examples.", "20 min · Practice"),
            ("Science", "Summarize one key concept in your own words and draw a diagram.", "15 min · Recall"),
            ("English", "Read one short passage and note its main idea and new vocabulary.", "15 min · Reading"),
            ("Computer", "Write a small algorithm as steps before trying it in code.", "20 min · Problem solving"),
        ], start=1)
    )

    page = f'''<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Student Performance | Campus Pulse</title>
    <style>
        :root {{ color-scheme:light; --ink:#182642; --muted:#748096; --line:#e7ebf2; --blue:#455ce9; --teal:#16a889; --paper:#f3f5f9; --gold:#efa83b; }}
        * {{ box-sizing:border-box; }} html {{ scroll-behavior:smooth; }} body {{ margin:0; background:radial-gradient(ellipse at 8% 18%,#e0e8ff 0,transparent 28%),radial-gradient(ellipse at 94% 42%,#daf4ec 0,transparent 25%),radial-gradient(ellipse at 50% 88%,#f2e9ff 0,transparent 32%),var(--paper); background-attachment:fixed; color:var(--ink); font:14px/1.5 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif; }}
        body::before {{ position:fixed; inset:0; z-index:-1; content:""; pointer-events:none; opacity:.2; background-image:radial-gradient(#8796b7 0.6px,transparent 0.6px); background-size:18px 18px; mask-image:linear-gradient(to bottom,transparent,#000 22%,#000 85%,transparent); }}
        .topbar {{ height:66px; padding:0 max(22px,calc((100vw - 1240px)/2)); display:flex; align-items:center; justify-content:space-between; background:white; border-bottom:1px solid var(--line); }}
        .brand {{ display:flex; align-items:center; gap:10px; font-size:15px; font-weight:800; letter-spacing:-.02em; }} .brand-mark {{ display:grid; place-items:center; width:34px; height:34px; color:white; background:var(--blue); border-radius:11px; }}
        nav {{ display:flex; gap:22px; }} nav a {{ color:#58647a; text-decoration:none; font-size:12px; font-weight:650; }} nav a:hover {{ color:var(--blue); }}
        .hero {{ position:relative; isolation:isolate; overflow:hidden; padding:36px max(22px,calc((100vw - 1240px)/2)); background:radial-gradient(circle at 82% 18%,#86a2ff55 0 2px,transparent 3px),radial-gradient(ellipse at 88% 110%,#27c5a555,transparent 34%),linear-gradient(112deg,#142443,#263f79 62%,#394d98); color:white; }} .hero::after {{ position:absolute; z-index:-1; right:7%; top:-88px; width:290px; height:290px; content:""; border:1px solid #ffffff22; border-radius:50%; box-shadow:0 0 0 30px #ffffff08,0 0 0 62px #ffffff06; }} .hero-line {{ display:flex; align-items:flex-end; justify-content:space-between; gap:20px; }}
        .eyebrow {{ color:#bdccff; font-size:10px; font-weight:800; letter-spacing:.14em; text-transform:uppercase; }} h1 {{ margin:6px 0; font-size:clamp(25px,3vw,34px); line-height:1.2; letter-spacing:-.035em; }} .hero p {{ margin:0; color:#d2dcf1; font-size:13px; }} .term-chip {{ padding:8px 12px; color:#e4eaff; border:1px solid #ffffff36; border-radius:9px; font-size:11px; white-space:nowrap; }}
        main {{ max-width:1240px; margin:22px auto; padding:0 22px 48px; }} section {{ scroll-margin-top:16px; }} .section-heading {{ display:flex; align-items:end; justify-content:space-between; margin:0 0 12px; }} h2 {{ margin:0; font-size:17px; letter-spacing:-.02em; }} .section-note {{ color:var(--muted); font-size:11px; }}
        .stats {{ display:grid; grid-template-columns:repeat(4,1fr); gap:12px; }} .card,.panel {{ border:1px solid var(--line); border-radius:13px; background:white; box-shadow:0 4px 16px #24365508; }}
        .card {{ padding:16px 18px; }} .card-label {{ display:flex; justify-content:space-between; color:var(--muted); font-size:11px; }} .card strong {{ display:block; margin-top:7px; font-size:26px; letter-spacing:-.04em; }} .card strong small {{ font-size:14px; }} .stat-accent {{ color:var(--teal); font-size:10px; }}
        .grid-2 {{ display:grid; grid-template-columns:1fr 1fr; gap:14px; margin-top:15px; }} .grid-3 {{ display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin-top:15px; }} .panel {{ position:relative; padding:18px; min-width:0; background:#ffffffec; backdrop-filter:blur(8px); }} .panel-title {{ margin:0 0 14px; font-size:14px; }}
        .subject-grid {{ display:grid; grid-template-columns:repeat(2,1fr); gap:10px; }} .subject-card {{ padding:12px; border:1px solid var(--line); border-radius:10px; }} .subject-top {{ display:flex; align-items:center; justify-content:space-between; }} .subject-icon {{ display:grid; place-items:center; width:27px; height:27px; border-radius:9px; color:var(--blue); background:#eef0ff; font-weight:800; }} .subject-score {{ color:#19866f; font-weight:800; font-size:14px; }} .subject-card h3 {{ margin:8px 0 1px; font-size:13px; }} .subject-card p {{ margin:0 0 9px; color:var(--muted); font-size:10px; }} .subject-card small {{ display:block; margin-top:5px; color:var(--muted); font-size:9px; }}
        .bar-track {{ height:7px; overflow:hidden; border-radius:10px; background:#edf0f6; }} .bar {{ height:100%; border-radius:10px; background:linear-gradient(90deg,#455ce9,#20b49a); }} .attendance-bar {{ background:linear-gradient(90deg,#16a889,#7bcead); }}
        .grade-row {{ display:grid; grid-template-columns:38px 1fr 22px; align-items:center; gap:8px; margin:9px 0; font-size:10px; }} .grade-label {{ color:var(--blue); font-weight:850; }} .grade-row strong {{ text-align:right; }} .grade-bar {{ background:linear-gradient(90deg,#8973ee,#51bda8); }} .class-pulse {{ display:grid; grid-template-columns:repeat(3,1fr); gap:8px; margin-top:13px; }} .pulse-item {{ padding:10px; border-radius:9px; background:linear-gradient(145deg,#f6f7ff,#f2fbf8); }} .pulse-item span {{ display:block; color:var(--muted); font-size:9px; }} .pulse-item strong {{ display:block; margin-top:3px; font-size:13px; }}
        .attendance-row {{ display:grid; grid-template-columns:155px 1fr 75px; align-items:center; gap:10px; margin:15px 0; font-size:11px; }} .attendance-row strong {{ text-align:right; font-size:10px; }} .attendance-legend {{ padding-top:8px; color:var(--muted); font-size:10px; }}
        .profile-list {{ display:grid; gap:8px; }} .student-profile {{ overflow:hidden; border:1px solid var(--line); border-radius:10px; background:#fff; }} .student-profile summary {{ display:flex; align-items:center; gap:11px; padding:11px 13px; cursor:pointer; list-style:none; }} .student-profile summary::-webkit-details-marker {{ display:none; }} .student-profile summary::after {{ content:"＋"; margin-left:3px; color:var(--blue); font-size:16px; }} .student-profile[open] summary::after {{ content:"−"; }} .avatar {{ display:grid; flex:0 0 37px; place-items:center; width:37px; height:37px; border-radius:13px; color:white; background:linear-gradient(140deg,#5369ec,#19aa91); font-size:15px; font-weight:800; }} .profile-heading {{ flex:1; }} .profile-heading strong,.profile-heading small {{ display:block; }} .profile-heading strong {{ font-size:12px; }} .profile-heading small {{ color:var(--muted); font-size:9px; }} .profile-quick {{ color:var(--muted); font-size:9px; }} .profile-quick strong {{ display:block; color:var(--ink); font-size:11px; }} .profile-status {{ padding:4px 8px; border-radius:20px; background:#e9f8f2; color:#087a5d; font-size:8px; font-weight:800; white-space:nowrap; }} .profile-status.fail-status {{ background:#fff0ee; color:#bd3b32; }} .profile-details {{ padding:0 14px 12px 61px; }} .mark-list {{ display:grid; grid-template-columns:repeat(4,1fr); gap:7px 12px; }} .mark-item {{ display:flex; align-items:center; justify-content:space-between; gap:8px; font-size:10px; }} .mark-item strong {{ font-size:10px; }} .profile-tip {{ margin:10px 0 0; padding:9px 10px; border-radius:8px; color:#3e5380; background:#f1f5ff; font-size:10px; }}
        table {{ width:100%; border-collapse:collapse; text-align:left; font-size:11px; }} th,td {{ padding:9px 8px; border-bottom:1px solid var(--line); white-space:nowrap; }} th {{ color:var(--muted); font-size:9px; letter-spacing:.04em; text-transform:uppercase; }} .grade {{ display:inline-block; padding:3px 8px; border-radius:20px; background:#eef2ff; color:var(--blue); font-weight:800; }} .result {{ padding:3px 7px; border-radius:20px; font-size:9px; font-weight:800; }} .pass {{ background:#e9f8f2; color:#087a5d; }} .fail {{ background:#fff0ee; color:#bd3b32; }} .table-panel {{ overflow:auto; }}
        .alert-card {{ display:flex; align-items:flex-start; gap:10px; padding:11px 12px; margin:8px 0; border:1px solid #f1e4c9; border-left:3px solid var(--gold); border-radius:9px; background:#fffcf6; }} .alert-icon {{ color:#bd7a10; font-size:15px; }} .alert-card p {{ margin:3px 0; color:#5f6572; font-size:10px; }} .alert-card small {{ color:var(--muted); font-size:10px; }} .student-id {{ margin-left:7px; color:var(--muted); font-size:9px; }}
        .event-list {{ display:grid; gap:9px; }} .event-card {{ display:flex; align-items:center; gap:11px; padding:11px; border:1px solid var(--line); border-radius:10px; }} .event-date {{ display:grid; flex:0 0 45px; place-items:center; min-height:44px; padding:4px; border-radius:9px; background:#f0f2ff; color:var(--blue); font-size:9px; font-weight:900; text-align:center; }} .event-info {{ flex:1; min-width:0; }} .event-type {{ color:#228b78; font-size:9px; font-weight:800; text-transform:uppercase; }} .event-info h3 {{ margin:2px 0; font-size:11px; }} .event-info p {{ margin:0; color:var(--muted); font-size:9px; }} .invite-tag {{ padding:6px 8px; border:1px solid #dfe4ff; border-radius:7px; background:#f5f6ff; color:var(--blue); font-size:8px; font-weight:750; white-space:nowrap; }}
        .study-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }} .study-card {{ position:relative; min-height:133px; padding:14px; border:1px solid var(--line); border-radius:10px; background:linear-gradient(150deg,#fff,#fafbff); }} .study-number {{ color:#b5bef7; font-size:10px; font-weight:900; }} .study-card h3 {{ margin:7px 0 4px; font-size:12px; }} .study-card p {{ min-height:35px; margin:0; color:#667187; font-size:10px; }} .study-time {{ display:inline-block; margin-top:9px; color:#18846f; font-size:9px; font-weight:800; }}
        .week-grid {{ display:grid; grid-template-columns:repeat(5,1fr); gap:8px; }} .day-card {{ min-height:106px; padding:11px; border:1px solid var(--line); border-radius:10px; background:linear-gradient(155deg,#fff,#f8f9ff); }} .day-name {{ color:var(--blue); font-size:9px; font-weight:850; letter-spacing:.08em; text-transform:uppercase; }} .day-card strong {{ display:block; margin:6px 0 3px; font-size:11px; }} .day-card p {{ margin:0; color:var(--muted); font-size:9px; }} .day-card.rest {{ background:linear-gradient(155deg,#f1fbf7,#fff); }}
        .community-grid {{ display:grid; grid-template-columns:repeat(3,1fr); gap:10px; }} .community-card {{ padding:13px; border:1px solid var(--line); border-radius:10px; background:linear-gradient(145deg,#fff,#fafaff); }} .community-icon {{ display:grid; place-items:center; width:31px; height:31px; border-radius:10px; background:#eef0ff; color:var(--blue); font-weight:850; }} .community-card h3 {{ margin:8px 0 4px; font-size:12px; }} .community-card p {{ margin:0; color:var(--muted); font-size:10px; }} .community-tag {{ display:inline-block; margin-top:9px; padding:3px 7px; border-radius:20px; color:#18846f; background:#e9f8f2; font-size:8px; font-weight:850; }}
        .method-grid {{ display:grid; grid-template-columns:repeat(4,1fr); gap:10px; }} .method-item {{ padding:12px; border-left:2px solid #8791ee; background:#f7f8ff; border-radius:0 8px 8px 0; }} .method-item strong {{ display:block; font-size:10px; }} .method-item p {{ margin:4px 0 0; color:var(--muted); font-size:9px; }} .closing-note {{ margin-top:14px; padding:14px 16px; border-radius:10px; color:#3e5380; background:linear-gradient(110deg,#edf2ff,#effaf6); font-size:10px; }}
        .stack-strip {{ display:flex; flex-wrap:wrap; align-items:center; gap:8px; margin:0 0 13px; padding:10px 12px; border:1px solid #e8ebfa; border-radius:9px; background:#f8f9ff; }} .stack-strip span {{ margin-right:4px; color:var(--muted); font-size:9px; font-weight:800; letter-spacing:.08em; }} .stack-strip strong {{ padding:4px 9px; border-radius:20px; color:#394cae; background:#e9edff; font-size:9px; }} .stack-strip small {{ color:var(--muted); font-size:9px; }}
        footer {{ padding:18px 0 0; color:var(--muted); font-size:10px; }}
        @media(max-width:900px) {{ nav {{ gap:11px; }} nav a {{ font-size:10px; }} .grid-3 {{ grid-template-columns:1fr 1fr; }} .study-grid {{ grid-template-columns:repeat(2,1fr); }} .method-grid {{ grid-template-columns:repeat(2,1fr); }} }}
        @media(max-width:650px) {{ .topbar {{ height:auto; min-height:60px; flex-wrap:wrap; padding:12px 18px; gap:10px; }} nav {{ width:100%; overflow:auto; padding-bottom:3px; }} nav a {{ flex:0 0 auto; }} .hero-line {{ align-items:flex-start; flex-direction:column; }} main {{ margin-top:15px; padding:0 14px 35px; }} .stats {{ grid-template-columns:repeat(2,1fr); }} .grid-2,.grid-3 {{ grid-template-columns:1fr; }} .attendance-row {{ grid-template-columns:125px 1fr 69px; gap:7px; }} .panel {{ padding:14px; }} .subject-grid {{ gap:7px; }} .week-grid {{ grid-template-columns:repeat(2,1fr); }} .community-grid {{ grid-template-columns:1fr; }} .class-pulse {{ grid-template-columns:1fr; }} .profile-details {{ padding-left:13px; }} .profile-quick {{ display:none; }} .mark-list {{ grid-template-columns:repeat(2,1fr); }} .invite-tag {{ display:none; }} }}
    </style>
</head>
<body>
    <div class="topbar"><div class="brand"><span class="brand-mark">CP</span> Campus Pulse</div>
        <nav aria-label="Dashboard sections"><a href="#overview">Overview</a><a href="#profile">Student account</a><a href="#subjects">Subjects & lecturers</a><a href="#events">Invitations</a><a href="#planner">Study planner</a><a href="#community">Campus life</a><a href="#records">Student records</a></nav>
    </div>
    <header class="hero"><div class="hero-line"><div><div class="eyebrow">Learning insights · Class 12-A</div>
        <h1>Student success, in focus.</h1><p>A friendly academic pulse for progress, participation, and opportunities.</p></div>
        <div class="term-chip">DEMO TERM · NOV 2026</div></div></header>
    <main>
        <section id="overview" class="stats">
            <article class="card"><div class="card-label"><span>Students in this view</span><span class="stat-accent">● Updated from CSV</span></div><strong>{len(results)}</strong></article>
            <article class="card"><div class="card-label"><span>Class marks average</span><span class="stat-accent">Across {len(SUBJECTS)} subjects</span></div><strong>{class_average:.1f}<small>%</small></strong></article>
            <article class="card"><div class="card-label"><span>Pass / needs support</span><span class="stat-accent">Per-subject pass rule</span></div><strong>{passed}<small> / {failed}</small></strong></article>
            <article class="card"><div class="card-label"><span>Attendance follow-ups</span><span class="stat-accent">Below {LOW_ATTENDANCE_LIMIT}%</span></div><strong>{attendance_bands['Follow up · below 75%']}</strong></article>
        </section>

        <section class="grid-2">
            <article class="panel"><div class="section-heading"><h2>Attendance pulse</h2><span class="section-note">Class attendance bands</span></div>
                {attendance_rows}<div class="attendance-legend">Flags are reminders to check in, not conclusions about a student.</div></article>
            <article class="panel"><div class="section-heading"><h2>Class standouts</h2><span class="section-note">Top averages · passing all subjects</span></div>
                <table><thead><tr><th>Student</th><th>Average marks</th><th>Grade</th></tr></thead><tbody>{top_rows}</tbody></table></article>
        </section>

        <section class="grid-2">
            <article class="panel"><div class="section-heading"><h2>Grade constellation</h2><span class="section-note">A quick view of this class cohort</span></div>{grade_rows}</article>
            <article class="panel"><div class="section-heading"><h2>Class learning map</h2><span class="section-note">Patterns in the current sample</span></div>
                <p class="section-note">A useful starting point for choosing class-wide revision activities.</p>
                <div class="class-pulse"><div class="pulse-item"><span>Average attendance</span><strong>{average_attendance:.1f}%</strong></div>
                    <div class="pulse-item"><span>Bright spot</span><strong>{escape(strongest_subject)}</strong></div>
                    <div class="pulse-item"><span>Shared practice focus</span><strong>{escape(focus_subject)}</strong></div></div>
                <div class="closing-note">Try a short {escape(focus_subject)} recap as a class, then invite students to choose one question they want to explore further.</div>
            </article>
        </section>

        <section id="profile" class="panel" style="margin-top:15px"><div class="section-heading"><h2>Student account · Academic profiles</h2><span class="section-note">Expand a fictional student record · academic details only</span></div>
            <div class="profile-list">{profile_cards}</div></section>

        <section id="subjects" class="grid-2">
            <article class="panel"><div class="section-heading"><h2>Subjects & lecturers</h2><span class="section-note">Teacher name and class marks percentage</span></div><div class="subject-grid">{subject_cards}</div></article>
            <article class="panel"><div class="section-heading"><h2>Attendance & marks alerts</h2><span class="section-note">Supportive review list · {alert_count} students</span></div>{alert_cards}</article>
        </section>

        <section id="events" class="grid-2">
            <article class="panel"><div class="section-heading"><h2>Invitations & campus moments</h2><span class="section-note">Fictional demo calendar · Nov 2026</span></div><div class="event-list">{event_cards}</div></article>
            <article class="panel"><div class="section-heading"><h2>Small steps study studio</h2><span class="section-note">Practical 15–20 minute revision ideas</span></div><div class="study-grid">{study_cards}</div></article>
        </section>

        <section id="planner" class="panel" style="margin-top:15px"><div class="section-heading"><div><h2>Five-day focus rhythm</h2><span class="section-note">An optional sample routine · adjust around your own timetable and rest</span></div><span class="section-note">Small, repeatable steps beat last-minute cramming</span></div>
            <div class="week-grid">
                <article class="day-card"><span class="day-name">Monday · Reset</span><strong>Pick one focus topic</strong><p>Write a tiny goal for the week and gather your class notes.</p></article>
                <article class="day-card"><span class="day-name">Tuesday · Practice</span><strong>Try, check, retry</strong><p>Spend 20 minutes on a few Maths or Computer questions.</p></article>
                <article class="day-card"><span class="day-name">Wednesday · Recall</span><strong>Explain it simply</strong><p>Summarize one Science idea without looking at your notes.</p></article>
                <article class="day-card"><span class="day-name">Thursday · Connect</span><strong>Read and discuss</strong><p>Review an English passage or ask a classmate a question.</p></article>
                <article class="day-card rest"><span class="day-name">Friday · Reflect</span><strong>Notice your progress</strong><p>Celebrate one win, note one question, then make time to rest.</p></article>
            </div>
        </section>

        <section id="community" class="panel" style="margin-top:15px"><div class="section-heading"><div><h2>Beyond the classroom</h2><span class="section-note">A balanced student experience includes curiosity, connection, and rest.</span></div><span class="section-note">Fictional opportunities for the mini-project demo</span></div>
            <div class="community-grid">
                <article class="community-card"><span class="community-icon">01</span><h3>Peer learning circle</h3><p>Bring one question, explain one idea to a friend, and learn together without competition.</p><span class="community-tag">COLLABORATION</span></article>
                <article class="community-card"><span class="community-icon">02</span><h3>Creative campus fest</h3><p>Explore a coding, science, arts, or presentation activity beyond regular classwork.</p><span class="community-tag">CURIOSITY</span></article>
                <article class="community-card"><span class="community-icon">03</span><h3>Ask-a-lecturer hour</h3><p>Use a question hour to clarify a topic or talk through a practical study strategy.</p><span class="community-tag">ASK FOR SUPPORT</span></article>
            </div>
        </section>

        <section class="panel" style="margin-top:15px"><div class="section-heading"><div><h2>How to read this learning snapshot</h2><span class="section-note">Transparent rules make the dashboard easier to discuss in a classroom presentation.</span></div></div>
            <div class="stack-strip"><span>ANALYTICS STACK</span><strong>Python</strong><strong>NumPy</strong><strong>Pandas</strong><small>Static HTML/CSS is used only to display the generated page; no JavaScript or web framework.</small></div>
            <div class="method-grid">
                <article class="method-item"><strong>Marks average</strong><p>The mean of the listed subject marks. Subject-level results are still shown separately.</p></article>
                <article class="method-item"><strong>Pass / support</strong><p>Pass requires each listed subject to meet the configured pass mark of {PASS_MARK}.</p></article>
                <article class="method-item"><strong>Attendance flag</strong><p>Attendance below {LOW_ATTENDANCE_LIMIT}% prompts a check-in; it does not explain why attendance changed.</p></article>
                <article class="method-item"><strong>Study suggestions</strong><p>Simple examples based on marks and attendance. A lecturer should consider each student's context.</p></article>
            </div>
            <div class="closing-note"><strong>Designed for people, not labels.</strong> This mini-project uses fictional student names, lecturer names, and campus events. Its summaries are classroom discussion aids—not official grades, diagnoses, or automated decisions.</div>
        </section>

        <section id="records" class="panel table-panel" style="margin-top:15px"><div class="section-heading"><div><h2>Student marks & attendance records</h2><span class="section-note">All fictional student rows · marks shown as percentages</span></div></div>
            <table><thead><tr><th>ID</th><th>Student</th><th>Average</th><th>Grade</th><th>Result</th><th>Attend.</th>{''.join(f'<th>{escape(subject)}</th>' for subject in SUBJECTS)}<th>Focus area</th></tr></thead><tbody>{table_rows}</tbody></table></section>
        <footer>All names and campus activities in this demo are fictional. Early-warning indicators are prompts for a supportive human check-in; they are not diagnoses or automated decisions.</footer>
    </main>
</body>
</html>'''
    output_path.write_text(page, encoding="utf-8")
    print(f"Browser dashboard saved to: {output_path}")


def main() -> None:
    """Run the complete workflow from CSV input to dashboard and report."""
    parser = argparse.ArgumentParser(description="Analyze student marks and attendance from a CSV file.")
    parser.add_argument("--input", type=Path, default=DATA_FILE, help="Path to the student dataset CSV")
    parser.add_argument("--output", type=Path, default=REPORT_FILE, help="Path for the generated report CSV")
    args = parser.parse_args()

    try:
        students = load_student_data(args.input)
        results = analyze_students(students)
        print_dashboard(results)
        save_report(results, args.output)
        save_html_dashboard(results, HTML_REPORT_FILE)
    except (FileNotFoundError, ValueError, pd.errors.ParserError) as error:
        parser.error(str(error))


if __name__ == "__main__":
    main()

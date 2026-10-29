"""Small checks for the project rules and data calculations."""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import pandas as pd

from main import analyze_students, calculate_grade, load_student_data, save_html_dashboard


class StudentAnalyticsTests(unittest.TestCase):
    def test_grade_boundaries(self):
        self.assertEqual(calculate_grade(90), "A+")
        self.assertEqual(calculate_grade(80), "A")
        self.assertEqual(calculate_grade(39.9), "F")

    def test_each_subject_must_be_passed(self):
        students = pd.DataFrame(
            [{"student_id": "T1", "name": "Test Student", "class": "12-A",
              "attendance_pct": 90, "Maths": 39, "Science": 90,
              "English": 90, "Computer": 90}]
        )
        result = analyze_students(students).iloc[0]
        self.assertEqual(result["result"], "FAIL")
        self.assertEqual(result["weakest_subject"], "Maths")
        self.assertIn("Subject mark below pass mark", result["early_warning"])

    def test_sample_dataset_has_expected_rows(self):
        students = load_student_data(Path("data/students.csv"))
        self.assertEqual(len(students), 30)
        self.assertEqual(
            students["name"].tolist(),
            [
                "samba", "shiva", "manvish", "vishal", "vijay", "srija",
                "minnu", "sathvika", "ammu", "swapna", "prasanna", "vikranth",
                "vikas", "vivek", "chandu", "patan", "anjali", "pravalika",
                "ashu", "charitha", "akshitha", "ramya", "rahul", "tinku",
                "kanna", "poorna", "snehith", "pranay", "charan", "dora",
            ],
        )

    def test_html_dashboard_includes_student_portal_sections(self):
        students = analyze_students(load_student_data(Path("data/students.csv")))
        with TemporaryDirectory() as folder:
            output_path = Path(folder) / "dashboard.html"
            save_html_dashboard(students, output_path)
            page = output_path.read_text(encoding="utf-8")

        for section in (
            "Student account", "Subjects & lecturers", "Attendance pulse",
            "Invitations & campus moments", "Student marks & attendance records",
            "Demo invitation", "samba", "Ms. Kavita Rao", "Innovation &amp; Coding Fest",
            "Grade constellation", "Five-day focus rhythm", "Beyond the classroom",
            "How to read this learning snapshot", "ANALYTICS STACK", "Python", "NumPy", "Pandas",
            "background:radial-gradient",
        ):
            with self.subTest(section=section):
                self.assertIn(section, page)
        self.assertNotIn("<script", page)
        self.assertNotIn("onclick=", page)


if __name__ == "__main__":
    unittest.main()

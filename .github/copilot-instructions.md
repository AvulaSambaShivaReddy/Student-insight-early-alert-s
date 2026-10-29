# Workspace instructions

## Project
Student Performance Analytics & Early Warning System is a beginner-friendly Python command-line mini-project. It uses Python, NumPy, Pandas, and fictional CSV input data; do not introduce web frameworks, databases, machine learning, or unnecessary dependencies.

## Conventions
- Keep analysis logic and static HTML report generation in reusable, clearly named functions in `main.py`; do not add a web server or framework.
- Keep fictional sample student marks and attendance in `data/students.csv`; preserve the required column names and 0–100 validation. Lecturer names and campus events in the website are fictional demo content.
- Explain changes in beginner-friendly language and preserve the project's documented pass, grade, attendance, and alert rules unless explicitly asked to change them.
- Treat early-warning messages as supportive prompts for human follow-up, not diagnoses or automated decisions.
- Never add real or personally identifying student data to the repository. Student profiles must not include passwords, login credentials, or private contact information.

## Validation
- Install dependencies from `requirements.txt` in the workspace virtual environment.
- Run tests with `python -m unittest discover -s tests -v`.
- Run the application with `python main.py` from the project root.
- The VS Code task “Run Student Analytics Dashboard” runs the application using `.venv`.

## Setup checklist
- [x] Confirm project requirements and scaffold the project.
- [x] Implement the analytics, sample dataset, tests, and beginner documentation.
- [x] Install required Python packages; no VS Code extensions were needed for this setup.
- [x] Run all unit tests and the application successfully.
- [x] Create and run the dashboard task.
- [x] Verify README and project guide; document the GitHub publishing steps.

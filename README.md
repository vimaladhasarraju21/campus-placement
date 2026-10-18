# Campus Placement Management System

A full-stack web app for a college placement cell to replace spreadsheets/email/paper.

- **Backend:** Django + Django REST Framework + JWT auth, SQL database (SQLite by default, easy to swap for MySQL/Postgres)
- **Frontend:** React (Vite)
- **Roles:** Student, Company (recruiter), Admin (placement cell)

## What it does

- **Students** register (roll no., branch, CGPA), log in and land on a **home page of company cards**. Each
  card lists that company's open roles with an **Apply** button that opens a short apply form
  (phone, resume link, why interested). Branch/CGPA/deadline rules are enforced. **My Applications** tracks status.
- **Companies** register and wait for the placement cell. Their home page shows the **approval status**:
  - *Approved* -> approval date, **how many students applied** (shortlisted / selected / rejected) and applicants per job.
  - *Not approved* -> the **reason** the admin gave (or "waiting for approval" if not reviewed yet).
  Approved companies post jobs and shortlist/select/reject applicants.
- **Admin (placement cell)** approves or rejects companies (**rejection needs a reason**; the **date and admin
  name are stored**) and has a **Dashboard with two reports**:
  1. **Overall report (company-wise)** - every company with status, approved-on date, jobs, students applied,
     shortlisted/selected, and the list of students who applied (company -> students mapping).
  2. **Student report** - every student and which companies/roles they applied for (student -> companies mapping).
  Both reports are live (they read the database every time), can be searched/expanded, **downloaded as CSV**
  and printed.

## Demo data (so the reports are not empty)

`python manage.py seed_demo_data` creates 5 companies (3 approved on different dates, 1 pending, 1 rejected
with a reason), 7 jobs, 10 students and ~20 applications. It is safe to run repeatedly. Anything real users do
afterwards (register, apply, get approved...) appears in the same reports.

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `admin1234` |
| Student | `ananya`, `karthik`, `divya`, `rahul`, `meena`, `arjun`, `sneha`, `vikram`, `priya`, `suresh` | `Student@123` |
| Company | `infosys`, `zoho`, `tcs` (approved), `nextgen` (pending), `quickhire` (rejected) | `Company@123` |

---

## 0. What you need installed first (one-time)

1. **VS Code** — you already have this.
2. **Python 3.10+** — check with `python --version` in a VS Code terminal.
3. **Node.js 18+** — check with `node --version`.

That's it — **no database software to install.** This project uses **SQLite**, which is a real SQL
relational database (same tables, foreign keys, and queries as any other SQL database) that ships
built into Python, so there's nothing extra to download or configure. The database is just a single
file (`db.sqlite3`) that appears automatically inside `backend/` the first time you run migrations.

### Want to use MySQL instead?
If your college specifically wants to see MySQL, you can switch later with no rush:
1. Install MySQL Server or XAMPP, and make sure MySQL is running.
2. Create the database: `CREATE DATABASE campus_placement;`
3. In `backend/requirements.txt`, uncomment the `PyMySQL` line, then run `pip install -r requirements.txt` again.
4. In `backend/placement_system/settings.py`, comment out the SQLite `DATABASES` block and uncomment
   the MySQL one just below it.
5. Delete `db.sqlite3` if it exists, then re-run `python manage.py migrate`.
Everything else in the project — models, API, frontend — works identically either way.

## 1. Backend setup (Django) — do this once

Open the project folder in VS Code, then open a terminal (`` Ctrl+` ``) and run:

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Windows
# source venv/bin/activate       # Mac/Linux

pip install -r requirements.txt

python manage.py migrate          # migrations are already included in the repo

# Create the admin login + demo companies/students/applications
python manage.py seed_demo_data
```

## 2. Frontend setup (React) — do this once

Open a **second** VS Code terminal (keep the first one free) and run:

```bash
cd frontend
npm install
```

---

## 3. Running it for your demo (every time)

You need **two terminals running at the same time** in VS Code — the backend and frontend are separate
servers. Split the terminal panel (the little split-icon at top-right of the terminal) so you can see both.

**Terminal 1 — backend:**
```bash
cd backend
venv\Scripts\activate            # Windows (skip if already active)
python manage.py runserver
```
Leave this running — it prints `Starting development server at http://127.0.0.1:8000/`.

**Terminal 2 — frontend:**
```bash
cd frontend
npm run dev
```
It'll print a local address, usually `http://localhost:5173/`. **Ctrl+click that link** (or copy it into
Chrome/Edge) — that's the actual website. This is what you show your HOD.

## 4. Suggested demo script (for your HOD / viva)

1. Log in as **`ananya`** (student) -> home page shows **company cards** (Infosys, Zoho, TCS). Click **Apply**
   on a role -> fill the short form -> submit. The role now shows its status.
2. Log in as **`nextgen`** (company, pending) -> status page says *waiting for approval*.
   Log in as **`quickhire`** (company, rejected) -> status page shows the **rejection reason**.
3. Log in as **`infosys`** (company, approved) -> status page shows the **approval date** and **how many
   students applied**. Open *My Job Postings -> View applicants* and shortlist/select someone.
4. Log in as **`admin`** -> **Companies** -> approve `nextgen` (date is stored) or reject with a reason.
5. Admin **Dashboard & Reports** -> show **Report 1 (overall, company-wise)** and **Report 2 (student-wise)**,
   expand a row, **Download CSV**. Re-open the report after step 1/4 to show it updated live.

## Project structure

```
backend/
  placement_system/     Django project settings & root urls
  placements/            Main app: models, serializers, views, permissions, admin, urls
    reports.py             the two admin reports (JSON + CSV export)
    management/commands/   create_placement_admin, seed_demo_data
frontend/
  src/
    api.js               Axios instance + JWT refresh handling
    context/AuthContext.jsx
    components/          Layout (sidebar), StatusBadge
    pages/                Login, Register (student/company)
    pages/student/        Company cards + apply form (JobBoard), My Applications, My Profile
    pages/company/        Status dashboard, Job postings + applicants, Company Profile
    pages/admin/          Dashboard + the two reports, Students, Companies (approve/reject)
```

## Notes / next steps you may want

- Resumes are currently a URL field (e.g. a Google Drive link) rather than a file upload — wiring up
  actual file upload (Django `FileField` + `MEDIA_ROOT`) is a natural next step.
- Email notifications (new job posted, status changed) aren't wired up yet — Django's `send_mail` plus
  a task queue (Celery) would be the way to add that.
- For production: set `DEBUG = False`, move `SECRET_KEY` to an environment variable, restrict
  `ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS`, and switch to Postgres/MySQL.

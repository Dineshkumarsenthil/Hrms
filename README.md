# HRMS - Human Resource Management System

A full stack HRMS with role-based dashboards for Admin, HR and Employee. It covers employee management, attendance, leave, payroll with PDF salary slips, reports, notifications and audit logs.

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10+, Django 5.2, Django REST Framework, SimpleJWT, django-filter |
| Database | MySQL 8 / MariaDB 10.6+ (SQLite fallback for quick tests) |
| Frontend | React 18, Vite, Tailwind CSS 4, Axios, React Router |
| PDF | ReportLab |

## Setup

### 1. Database

```sql
CREATE DATABASE hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

To start with sample data instead of seeding, import the dump after creating the database:

```bash
mysql -u root -p hrms_db < database/hrms_db_dump.sql
```

### 2. Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Mac/Linux: cp .env.example .env
```

Edit `.env` and set `DB_PASSWORD`. If `DB_NAME` is left empty, Django uses SQLite.

```bash
python manage.py migrate
python manage.py seed_data
python manage.py runserver
```

The API runs at `http://127.0.0.1:8000/api/`.

### 3. Frontend

Open a new terminal:

```bash
cd frontend
npm install
npm run dev
```

The app runs at `http://localhost:5173`.

## Sample Credentials

| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| HR | `hr` | `Hr@12345` |
| Employee | `dinesh`, `priya`, `arun`, `meena` | `Employee@123` |

Email also works as the username, for example `hr@hrms.local`.

## Tests

```bash
cd backend
python manage.py test
```

## API

All endpoints are under `http://127.0.0.1:8000/api/`: `auth/`, `employees/`, `attendance/`, `leaves/`, `payroll/`, `notifications/`, `reports/` and `audit/`.

The full list of 53 requests is in `postman/HRMS.postman_collection.json`. Run a login request first, because it stores the token for the other requests.

## Project Structure

```
backend/    Django apps: accounts, employees, attendance, leaves, payroll,
            notifications, reports, audit, config
frontend/   React app: src/pages, src/components
database/   schema.sql, hrms_db_dump.sql
postman/    HRMS.postman_collection.json
docs/       sample_salary_slip.pdf, MODULE_NOTES.md
```
<<<<<<< HEAD
=======

## Submission checklist
- [ ] Push to GitHub (frontend + backend in one repo, `.gitignore` included)
- [x] Database schema + dump: `database/`
- [x] Postman collection: `postman/`
- [x] Sample credentials: above
- [x] Sample salary slip: `docs/sample_salary_slip.pdf`
- [ ] UI screenshots: log in as `admin` (Dashboard, Employees, Payroll) and `dinesh` (Dashboard, Salary Slips) and capture them

## Phase 2 - HRMS enhancements

New modules (all behind the existing JWT login and role checks, with audit logging on every change):

| Module | Backend app / API | Frontend |
|---|---|---|
| Holidays & calendar | `holidays` - `/api/holidays/?year=&month=` | Holidays page, calendar on the dashboard (month / year view) |
| In-app notifications | `notifications` - `/api/notifications/`, `/unread-count/`, `/mark-all-read/`, `/preferences/`, `/broadcasts/` | Bell in the top bar, Notifications page |
| Shifts & schedules | `shifts` - `/api/shifts/`, `/api/shifts/assignments/`, `/api/shifts/my-shift/`, `/api/reports/shift-attendance/` | Shifts page (shifts, assignments + history, shift report) |
| Advanced payroll | `payroll` - `/api/payroll/components/`, `/structures/`, `/variable-pay/` | Payroll page tabs, pay slip breakdown |

Rules worth knowing:

- **Holidays**: company holidays apply to everyone, regional holidays only to employees whose `region` matches, optional holidays never remove a working day. Working days (attendance, leave day count, payroll) skip weekends and these holidays.
- **Shifts**: a personal assignment beats a department assignment, which beats the default General Shift. Starting a new assignment closes the previous one, so old rows are the shift history. Late = check-in after start + grace. Early exit = check-out before the shift end. Overtime = hours worked beyond the length of the shift window (minimum 30 minutes). Night shifts can check out the next morning. Flexible shifts are never late / early.
- **Payroll**: gross comes from the salary structure in force for the month (employees without one use the salary fields on their profile). `net = gross + variable pay + overtime - LOP - deductions (+/- adjustment)`, never below zero. Overtime pay = overtime hours x (basic / working days / 8) x 1.5. Revising pay adds a new structure version (Admin only); generated payrolls keep their own copy of the breakdown (`PayrollLine`), so history never changes.
- **Roles**: Admin configures salary components, revises salaries and sends broadcasts. Admin and HR manage holidays, shifts, variable pay and see the reports. Employees only see their own notifications, shifts, structures and slips.

Upgrade an existing database with `python manage.py migrate` (adds the tables and seeds the default salary components and the General Shift). `database/*.sql` were exported for phase 1 and should be re-exported from your MySQL after migrating.

Run the tests: `python manage.py test` (use SQLite by leaving `DB_NAME` empty).
>>>>>>> 5cecf27 (Add HRMS enhancements)

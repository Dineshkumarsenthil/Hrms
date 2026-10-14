# HRMS - Human Resource Management System

Full stack HRMS: **Django REST Framework + MySQL** backend, **React + Tailwind** frontend.
Role-based dashboards (Admin / HR / Employee) for employees, attendance, leave, payroll, salary slips, notifications, reports and audit logs.

## Tech stack
| Layer | Tech |
|---|---|
| Backend | Python 3.10+, Django 5.2, Django REST Framework, SimpleJWT, django-filter |
| Database | MySQL 8 / MariaDB 10.6+ (SQLite fallback for quick tests) |
| Frontend | React 18, Vite, Tailwind CSS 4, Axios, React Router |
| PDF | ReportLab (salary slips + PDF reports) |

## Run it (step by step)

### 1. Database
```sql
CREATE DATABASE hrms_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2. Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate            # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
copy .env.example .env           # Mac/Linux: cp .env.example .env   -> then edit DB_PASSWORD
python manage.py migrate
python manage.py seed_data       # sample users, departments, leave types, last month's attendance
python manage.py runserver
```
API runs at http://127.0.0.1:8000/api/

*(No MySQL yet? Leave `DB_NAME` empty in `.env` and Django uses SQLite.)*

### 3. Frontend (new terminal)
```bash
cd frontend
npm install
npm run dev
```
Open http://localhost:5173

### 4. Import the ready-made database instead (optional)
```bash
mysql -u root -p hrms_db < database/hrms_db_dump.sql
```
The dump already contains users, last month's payroll (generated + credited), leave requests and attendance. Salary-slip PDFs for it are in `backend/media/slips/`.

## Sample credentials
| Role | Username | Password |
|---|---|---|
| Admin | `admin` | `Admin@123` |
| HR | `hr` | `Hr@12345` |
| Employee | `dinesh` | `Employee@123` |
| Employee | `priya`, `arun`, `meena` | `Employee@123` |

(Email also works as the username, e.g. `hr@hrms.local`.)

## Tests
```bash
cd backend
python manage.py test
```
Runs an end-to-end check (~95 assertions): login, role protection, employee CRUD + upload validation, duplicate check-in prevention, leave balance + LOP, payroll generation/locking/adjustment/credit, salary slip access control, CSV/PDF reports, audit log, token blacklist.

## Business rules
- **Working days** = Mon-Fri of the month, counted from the employee's joining date.
- **Attendance:** one record per employee per day (DB unique constraint). Hours >= 4 = Present, < 4 = Half day (0.5).
- **Leave:** weekends excluded. If days > remaining balance, the excess becomes **LOP** (unpaid leave types are fully LOP). Balance is deducted on approval and restored on cancellation.
- **Payroll** (completed months only):
  `LOP days = working days - present - paid leave`
  `LOP deduction = gross / working days x LOP days`
  `Net = gross - LOP deduction - PF (basic x PF%) - tax (+/- manual adjustment)`, never below 0.
- **Payroll lock:** records are locked on generation and cannot be regenerated. Only Admin can unlock, adjust (reason logged), and re-lock. Salary credit is a simulation (`SIM-...` reference), no payment gateway.

## Security
- Passwords hashed (PBKDF2), password validators on, no plain text anywhere (not even in the email log).
- JWT (30 min access, 1 day refresh, rotation + blacklist on logout). Login throttled to 10/min.
- Every endpoint requires a token; role checks on every sensitive endpoint; employees only ever see their own rows (queryset-level scoping).
- Uploads: extension allow-list, 5 MB limit, random file names, **not served publicly** (downloaded via an authenticated endpoint with ownership check).
- Input validated in serializers; uniform JSON error format; CSV export protected against formula injection.
- Audit log is append-only and exposed read-only.

## API
Full list in `postman/HRMS.postman_collection.json` (53 requests). Run a "Login" request first; it stores the token for the rest.
Base URL: `http://127.0.0.1:8000/api` - modules: `auth/`, `employees/`, `attendance/`, `leaves/`, `payroll/`, `notifications/`, `reports/`, `audit/`.

## Email
By default emails print in the backend terminal and are saved in the `EmailLog` table (visible under *Email Logs*). For real SMTP, set `EMAIL_HOST`, `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` in `.env`. Templates are stored in the DB and editable by Admin (`/api/notifications/templates/`).

## Project layout
```
backend/   accounts employees attendance leaves payroll notifications reports audit  config/
frontend/  src/pages (Dashboard, Employees, Attendance, Leaves, Payroll, Reports, Admin...)  src/components
database/  schema.sql, hrms_db_dump.sql
postman/   HRMS.postman_collection.json
docs/      sample_salary_slip.pdf, MODULE_NOTES.md
```

## Submission checklist
- [ ] Push to GitHub (frontend + backend in one repo, `.gitignore` included)
- [x] Database schema + dump: `database/`
- [x] Postman collection: `postman/`
- [x] Sample credentials: above
- [x] Sample salary slip: `docs/sample_salary_slip.pdf`
- [ ] UI screenshots: log in as `admin` (Dashboard, Employees, Payroll) and `dinesh` (Dashboard, Salary Slips) and capture them

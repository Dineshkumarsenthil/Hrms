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

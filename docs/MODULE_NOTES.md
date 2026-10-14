# Module notes (how each part works)

**accounts** - Custom `User` (role = ADMIN/HR/EMPLOYEE). Login uses SimpleJWT; the role is embedded in the token. Logout blacklists the refresh token. `permissions.py` has `IsAdmin`, `IsAdminOrHR`, `IsEmployee` used on views. Admin can change roles/activate users at `/auth/users/`.

**employees** - `Employee` links 1:1 to `User` and holds department, designation, joining date and salary structure (basic, HRA, allowances, PF %, tax). Creating an employee creates the login with a random temporary password, emails it (onboarding template) and shows it once to HR. Employees are deactivated, never deleted (payroll history must survive). Documents are validated (type, size), stored under a random name and only served through an authenticated view.

**attendance** - One row per employee per day (unique constraint prevents duplicate check-ins even under race conditions). Check-out computes hours and sets Present / Half day. HR/Admin corrections go through `/override/` and require a reason; they are flagged `is_overridden` and audit-logged. Monthly summary combines attendance with approved leave.

**leaves** - Leave types with yearly quota. Balances are created per employee per year on first use. Applying computes working days and splits any excess over balance into LOP days. Approval re-checks the balance inside a DB transaction (row locked), deducts it, and emails the employee. Reviewers can't approve their own requests. Cancelling a future approved leave restores the balance.

**payroll** - `services.compute()` calculates a month from attendance + approved leave. Generation creates a locked `Payroll` row (unique per employee/month) and a PDF `SalarySlip`, then emails the employee. Credit is simulated. Admin-only unlock -> adjust -> lock flow, every step audit-logged; the slip PDF is regenerated after an adjustment.

**notifications** - `send_templated(code, to, context)` renders a DB-stored Django template, sends it, and always writes an `EmailLog` row (SENT/FAILED). A mail failure never breaks the business action.

**reports** - Attendance, leave and payroll reports with date/department filters. `?format=json|csv|pdf`. Two dashboard endpoints feed the admin and employee home pages.

**audit** - `log_action()` is called from every critical action (login, CRUD, overrides, approvals, payroll steps, downloads, exports). The API exposes read-only list/detail only.

**frontend** - `api.js` attaches the JWT and silently refreshes it on a 401. `auth.jsx` holds the user; `App.jsx` guards routes by role; the sidebar changes per role. Pages use small shared hooks (`usePaged`, `useFetch`) from `components/ui.jsx`.

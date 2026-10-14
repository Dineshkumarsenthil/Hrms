"""End-to-end API smoke test: python manage.py shell < smoke_test.py  (or run via test runner)."""
import json, datetime, calendar
from django.test import Client
from django.utils import timezone

c = Client()
fails = []

def call(method, url, token=None, data=None, files=False, expect=None):
    kw = {"HTTP_AUTHORIZATION": f"Bearer {token}"} if token else {}
    fn = getattr(c, method)
    if method in ("post", "patch", "put") and not files:
        r = fn(url, data=json.dumps(data or {}), content_type="application/json", **kw)
    else:
        r = fn(url, data=data, **kw) if data is not None else fn(url, **kw)
    ok = expect is None or r.status_code == expect
    print(("PASS" if ok else "FAIL"), method.upper(), url, r.status_code, (r.content[:140].decode(errors="ignore") if not ok else ""))
    if not ok: fails.append((method, url, r.status_code))
    return r

def login(u, p):
    r = call("post", "/api/auth/login/", data={"username": u, "password": p}, expect=200)
    return r.json()["access"], r.json()["refresh"]

# auth
call("post", "/api/auth/login/", data={"username": "admin", "password": "wrong"}, expect=401)
call("get", "/api/employees/", expect=401)
adm, adm_r = login("admin", "Admin@123")
hr, _ = login("hr@hrms.local", "Hr@12345")
emp, emp_r = login("dinesh", "Employee@123")
priya, _ = login("priya", "Employee@123")
call("get", "/api/auth/me/", adm, expect=200)
# RBAC
call("get", "/api/employees/", emp, expect=403)
call("get", "/api/employees/", hr, expect=200)
call("get", "/api/audit/", emp, expect=403)
call("get", "/api/audit/", hr, expect=200)
call("post", "/api/audit/", adm, data={}, expect=405)
call("get", "/api/auth/users/", hr, expect=403)
call("get", "/api/auth/users/", adm, expect=200)
call("get", "/api/employees/me/", emp, expect=200)

# employees
depts = call("get", "/api/employees/departments/", hr, expect=200).json()
d = depts[0]["id"]
r = call("post", "/api/employees/", hr, data={"first_name": "Test", "last_name": "Person", "email": "test.person@hrms.local", "department": d, "designation": "Intern",
         "joining_date": "2026-01-05", "basic_salary": "20000", "hra": "8000", "allowances": "2000"}, expect=201)
new_id = r.json()["id"]; temp = r.json()["temporary_password"]
call("post", "/api/employees/", hr, data={"first_name": "Dup", "email": "test.person@hrms.local", "department": d, "designation": "x", "joining_date": "2026-01-05"}, expect=400)
call("post", "/api/employees/", hr, data={"first_name": "Neg", "email": "neg@hrms.local", "department": d, "designation": "x", "joining_date": "2026-01-05", "basic_salary": "-5"}, expect=400)
call("patch", f"/api/employees/{new_id}/", hr, data={"designation": "Associate"}, expect=200)
newtok, _ = login("test.person", temp)
call("delete", f"/api/employees/{new_id}/", hr, expect=405)

# document upload validation
from django.core.files.uploadedfile import SimpleUploadedFile
good = SimpleUploadedFile("id.pdf", b"%PDF-1.4 test", content_type="application/pdf")
r = call("post", f"/api/employees/{new_id}/documents/", hr, data={"title": "ID proof", "file": good}, files=True, expect=201)
doc_id = r.json()["id"]
bad = SimpleUploadedFile("evil.exe", b"MZ", content_type="application/octet-stream")
call("post", f"/api/employees/{new_id}/documents/", hr, data={"title": "bad", "file": bad}, files=True, expect=400)
big = SimpleUploadedFile("big.pdf", b"0" * (6 * 1024 * 1024), content_type="application/pdf")
call("post", f"/api/employees/{new_id}/documents/", hr, data={"title": "big", "file": big}, files=True, expect=400)
call("get", f"/api/employees/documents/{doc_id}/download/", hr, expect=200)
call("get", f"/api/employees/documents/{doc_id}/download/", emp, expect=403)
call("get", f"/api/employees/documents/{doc_id}/download/", newtok, expect=200)

# attendance
call("post", "/api/attendance/check-out/", emp, expect=400)
call("post", "/api/attendance/check-in/", emp, expect=201)
call("post", "/api/attendance/check-in/", emp, expect=400)  # duplicate
call("post", "/api/attendance/check-out/", emp, expect=200)
call("post", "/api/attendance/check-out/", emp, expect=400)
call("get", "/api/attendance/", emp, expect=200)
call("get", "/api/attendance/my-summary/", emp, expect=200)
call("get", "/api/attendance/summary/", hr, expect=200)
call("get", "/api/attendance/summary/", emp, expect=403)
eid = call("get", "/api/employees/?search=EMP004", hr).json()["results"][0]["id"]
call("post", "/api/attendance/override/", hr, data={"employee": eid, "date": "2026-09-01", "status": "PRESENT", "note": "Forgot to punch"}, expect=200)  # record already seeded -> update
call("post", "/api/attendance/override/", hr, data={"employee": eid, "date": "2026-09-01", "status": "PRESENT"}, expect=400)  # note required
call("post", "/api/attendance/override/", emp, data={"employee": eid, "date": "2026-09-01", "status": "PRESENT", "note": "x"}, expect=403)

# leaves
types = {t["name"]: t["id"] for t in call("get", "/api/leaves/types/", emp, expect=200).json()}
call("get", "/api/leaves/balances/", emp, expect=200)
start = (datetime.date.today() + datetime.timedelta(days=14))
while start.weekday() != 0: start += datetime.timedelta(days=1)
end = start + datetime.timedelta(days=13)   # 10 working days > 12? casual quota 12 -> make a 14-day span: 10 wd
r = call("post", "/api/leaves/requests/", emp, data={"leave_type": types["Casual Leave"], "start_date": str(start), "end_date": str(end), "reason": "Trip"}, expect=201)
lr = r.json(); print("   leave days", lr["days"], "lop", lr["lop_days"])
call("post", "/api/leaves/requests/", emp, data={"leave_type": types["Casual Leave"], "start_date": str(start), "end_date": str(start), "reason": "overlap"}, expect=400)
call("post", "/api/leaves/requests/", emp, data={"leave_type": types["Casual Leave"], "start_date": "2020-01-01", "end_date": "2020-01-02", "reason": "past"}, expect=400)
call("post", f"/api/leaves/requests/{lr['id']}/approve/", emp, data={}, expect=403)
call("post", f"/api/leaves/requests/{lr['id']}/approve/", hr, data={"remarks": "ok"}, expect=200)
call("post", f"/api/leaves/requests/{lr['id']}/approve/", hr, data={}, expect=400)  # already reviewed
b = {x["leave_type_name"]: x for x in call("get", "/api/leaves/balances/", emp).json()}
print("   casual balance after approval:", b["Casual Leave"]["used"], "/", b["Casual Leave"]["allocated"])
# LOP: unpaid leave type, reject path
s2 = end + datetime.timedelta(days=3)
while s2.weekday() != 0: s2 += datetime.timedelta(days=1)
r2 = call("post", "/api/leaves/requests/", priya, data={"leave_type": types["Loss of Pay"], "start_date": str(s2), "end_date": str(s2 + datetime.timedelta(days=1)), "reason": "personal"}, expect=201).json()
print("   LOP request lop_days:", r2["lop_days"])
call("post", f"/api/leaves/requests/{r2['id']}/reject/", hr, data={"remarks": "Busy period"}, expect=200)
call("post", f"/api/leaves/requests/{lr['id']}/cancel/", emp, expect=200)
b = {x["leave_type_name"]: x for x in call("get", "/api/leaves/balances/", emp).json()}
print("   casual used after cancel (should be 0.0):", b["Casual Leave"]["used"])
call("get", "/api/leaves/requests/", emp, expect=200)

# payroll
t = timezone.localdate(); lm = t.replace(day=1) - datetime.timedelta(days=1)
call("post", "/api/payroll/generate/", hr, data={"year": t.year, "month": t.month}, expect=400)  # current month not allowed
call("post", "/api/payroll/generate/", emp, data={"year": lm.year, "month": lm.month}, expect=403)
r = call("post", "/api/payroll/generate/", hr, data={"year": lm.year, "month": lm.month}, expect=201); print("  ", r.json()["generated"], "generated; skipped:", r.json()["skipped"])
r = call("post", "/api/payroll/generate/", hr, data={"year": lm.year, "month": lm.month}, expect=200); print("   regenerate ->", r.json()["generated"], "generated (locked)")
mine = call("get", "/api/payroll/", emp, expect=200).json()["results"]
assert len(mine) == 1 and mine[0]["employee_code"] == "EMP003", mine
p = mine[0]; print("   dinesh payroll: wd", p["working_days"], "present", p["present_days"], "lop", p["lop_days"], "net", p["net_salary"])
call("get", f"/api/payroll/{p['id']}/slip/", emp, expect=200)
other = call("get", "/api/payroll/", hr).json()["results"]
other_id = [x["id"] for x in other if x["employee_code"] == "EMP004"][0]
call("get", f"/api/payroll/{other_id}/slip/", emp, expect=404)   # cannot access another's slip
call("get", f"/api/payroll/{other_id}/slip/", hr, expect=200)
call("post", f"/api/payroll/{p['id']}/adjust/", adm, data={"amount": "500", "note": "bonus"}, expect=400)   # locked
call("post", f"/api/payroll/{p['id']}/unlock/", hr, data={"reason": "x"}, expect=403)   # admin only
call("post", f"/api/payroll/{p['id']}/unlock/", adm, data={"reason": "Bonus"}, expect=200)
r = call("post", f"/api/payroll/{p['id']}/adjust/", adm, data={"amount": "500", "note": "Spot bonus"}, expect=200); print("   net after adjust:", r.json()["net_salary"])
call("post", f"/api/payroll/{p['id']}/lock/", adm, expect=200)
call("post", f"/api/payroll/{p['id']}/credit/", hr, expect=200)
call("post", f"/api/payroll/{p['id']}/credit/", hr, expect=400)
call("post", f"/api/payroll/{p['id']}/unlock/", adm, data={"reason": "x"}, expect=400)

# reports + dashboards
for rep in ("attendance", "leaves", "payroll"):
    call("get", f"/api/reports/{rep}/", hr, expect=200)
    call("get", f"/api/reports/{rep}/?format=csv&department={d}", hr, expect=200)
    call("get", f"/api/reports/{rep}/?format=pdf&date_from=2026-01-01&date_to=2026-12-31", hr, expect=200)
call("get", "/api/reports/attendance/", emp, expect=403)
call("get", "/api/reports/dashboard/admin/", hr, expect=200)
call("get", "/api/reports/dashboard/employee/", emp, expect=200)

# notifications, audit, roles
call("get", "/api/notifications/logs/", hr, expect=200)
call("get", "/api/notifications/templates/", adm, expect=200)
call("get", "/api/notifications/templates/", hr, expect=403)
uid = [u for u in call("get", "/api/auth/users/", adm).json()["results"] if u["username"] == "priya"][0]["id"]
call("patch", f"/api/auth/users/{uid}/", adm, data={"role": "HR"}, expect=200)
call("patch", f"/api/auth/users/{uid}/", adm, data={"role": "EMPLOYEE"}, expect=200)
call("post", f"/api/employees/{new_id}/deactivate/", hr, expect=200)
call("post", "/api/auth/login/", data={"username": "test.person", "password": temp}, expect=401)  # deactivated
call("post", "/api/auth/change-password/", emp, data={"old_password": "Employee@123", "new_password": "Employee@123x"}, expect=200)
call("post", "/api/auth/change-password/", emp, data={"old_password": "nope", "new_password": "Whatever@1234"}, expect=400)
call("post", "/api/auth/logout/", adm, data={"refresh": adm_r}, expect=200)
call("post", "/api/auth/refresh/", data={"refresh": adm_r}, expect=401)   # blacklisted

from audit.models import AuditLog
from notifications.models import EmailLog
print("\nAudit rows:", AuditLog.objects.count(), "| Email logs:", EmailLog.objects.count(), "| failures:", len(fails))
for f in fails: print("  FAILED:", f)

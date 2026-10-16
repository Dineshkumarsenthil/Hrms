from datetime import date, timedelta

from django.test import TestCase

from config.testing import client_for, make_department, make_employee, make_user
from leaves.models import LeaveType
from .inapp import notify, send_broadcast
from .models import Notification


class InboxTests(TestCase):
    def setUp(self):
        self.a = make_employee()
        self.b = make_employee()
        self.api_a, self.api_b = client_for(self.a.user), client_for(self.b.user)
        notify(self.a.user, "LEAVE", "Leave approved", "Your leave was approved", "/leaves")
        notify(self.a.user, "PAYROLL", "Payroll", "Slip ready", "/payroll")
        notify(self.b.user, "LEAVE", "Other person", "Not for A")

    def test_user_only_sees_own_notifications(self):
        rows = self.api_a.get("/api/notifications/").json()["results"]
        self.assertEqual(len(rows), 2)
        self.assertNotIn("Other person", [r["title"] for r in rows])

    def test_cannot_open_or_mark_someone_elses_notification(self):
        other_id = Notification.objects.get(user=self.b.user).id
        self.assertEqual(self.api_a.get(f"/api/notifications/{other_id}/").status_code, 404)
        self.assertEqual(self.api_a.post(f"/api/notifications/{other_id}/mark-read/").status_code, 404)
        self.assertEqual(self.api_a.delete(f"/api/notifications/{other_id}/").status_code, 404)

    def test_unread_count_and_mark_read(self):
        self.assertEqual(self.api_a.get("/api/notifications/unread-count/").json()["unread"], 2)
        first = Notification.objects.filter(user=self.a.user).first()
        r = self.api_a.post(f"/api/notifications/{first.id}/mark-read/")
        self.assertTrue(r.json()["is_read"])
        self.assertIsNotNone(r.json()["read_at"])
        self.assertEqual(self.api_a.get("/api/notifications/unread-count/").json()["unread"], 1)
        self.assertEqual(self.api_a.get("/api/notifications/?is_read=false").json()["count"], 1)

    def test_mark_all_read_only_touches_own(self):
        self.assertEqual(self.api_a.post("/api/notifications/mark-all-read/").json()["marked"], 2)
        self.assertEqual(self.api_b.get("/api/notifications/unread-count/").json()["unread"], 1)

    def test_requires_login(self):
        from rest_framework.test import APIClient
        self.assertEqual(APIClient().get("/api/notifications/").status_code, 401)


class PreferenceTests(TestCase):
    def setUp(self):
        self.emp = make_employee()
        self.api = client_for(self.emp.user)

    def test_all_kinds_enabled_by_default(self):
        prefs = self.api.get("/api/notifications/preferences/").json()
        self.assertTrue(all(p["enabled"] for p in prefs))
        self.assertGreaterEqual(len(prefs), 5)

    def test_disabled_kind_is_not_delivered(self):
        r = self.api.put("/api/notifications/preferences/", [{"kind": "LEAVE", "enabled": False}], format="json")
        self.assertFalse(next(p for p in r.json() if p["kind"] == "LEAVE")["enabled"])
        self.assertIsNone(notify(self.emp.user, "LEAVE", "Hidden", "should not be stored"))
        self.assertIsNotNone(notify(self.emp.user, "PAYROLL", "Shown", "still delivered"))
        self.assertEqual(Notification.objects.filter(user=self.emp.user).count(), 1)

    def test_can_switch_back_on(self):
        self.api.put("/api/notifications/preferences/", [{"kind": "LEAVE", "enabled": False}], format="json")
        self.api.put("/api/notifications/preferences/", [{"kind": "LEAVE", "enabled": True}], format="json")
        self.assertIsNotNone(notify(self.emp.user, "LEAVE", "Back", "on again"))

    def test_invalid_kind_rejected(self):
        r = self.api.put("/api/notifications/preferences/", [{"kind": "NOPE", "enabled": False}], format="json")
        self.assertEqual(r.status_code, 400)


class BroadcastTests(TestCase):
    def setUp(self):
        self.admin_user = make_user("ADMIN")
        self.admin = client_for(self.admin_user)
        self.eng, self.fin = make_department("Eng"), make_department("Fin")
        self.e1, self.e2 = make_employee(department=self.eng), make_employee(department=self.eng)
        self.f1 = make_employee(department=self.fin)

    def test_only_admin_can_broadcast(self):
        body = {"title": "Office closed", "message": "Closed on Friday"}
        self.assertEqual(client_for(make_user("HR")).post("/api/notifications/broadcasts/", body, format="json").status_code, 403)
        self.assertEqual(client_for(self.e1.user).post("/api/notifications/broadcasts/", body, format="json").status_code, 403)
        self.assertEqual(self.admin.post("/api/notifications/broadcasts/", body, format="json").status_code, 201)

    def test_whole_organization(self):
        r = self.admin.post("/api/notifications/broadcasts/", {"title": "Hello", "message": "All hands"}, format="json")
        total = Notification.objects.filter(kind="ANNOUNCEMENT").count()
        self.assertEqual(r.json()["recipient_count"], total)
        for emp in (self.e1, self.e2, self.f1):
            self.assertTrue(Notification.objects.filter(user=emp.user, title="Hello").exists())

    def test_department_only(self):
        r = self.admin.post("/api/notifications/broadcasts/", {"title": "Eng only", "message": "Deploy freeze", "department": self.eng.id}, format="json")
        self.assertEqual(r.json()["recipient_count"], 2)
        self.assertFalse(Notification.objects.filter(user=self.f1.user, title="Eng only").exists())

    def test_muted_users_are_skipped(self):
        client_for(self.e1.user).put("/api/notifications/preferences/", [{"kind": "ANNOUNCEMENT", "enabled": False}], format="json")
        r = self.admin.post("/api/notifications/broadcasts/", {"title": "Eng", "message": "msg", "department": self.eng.id}, format="json")
        self.assertEqual(r.json()["recipient_count"], 1)

    def test_validation_and_audit(self):
        self.assertEqual(self.admin.post("/api/notifications/broadcasts/", {"title": "  ", "message": "x"}, format="json").status_code, 400)
        self.assertEqual(self.admin.post("/api/notifications/broadcasts/", {"title": "x", "message": ""}, format="json").status_code, 400)
        self.admin.post("/api/notifications/broadcasts/", {"title": "Audit me", "message": "x"}, format="json")
        from audit.models import AuditLog
        self.assertTrue(AuditLog.objects.filter(action="BROADCAST_SEND").exists())

    def test_inactive_users_do_not_receive(self):
        self.f1.user.is_active = False
        self.f1.user.save()
        send_broadcast(self.admin_user, "Hi", "msg")
        self.assertFalse(Notification.objects.filter(user=self.f1.user).exists())


class EventHookTests(TestCase):
    """Real actions create notifications: leave request, approval, rejection."""

    def setUp(self):
        self.hr_user = make_user("HR")
        self.emp = make_employee()
        LeaveType.objects.create(name="Casual Leave", annual_quota=12, is_paid=True)
        self.monday = date.today() + timedelta(days=(7 - date.today().weekday()))

    def apply_leave(self):
        body = {"leave_type": LeaveType.objects.first().id, "start_date": str(self.monday), "end_date": str(self.monday), "reason": "Family function"}
        return client_for(self.emp.user).post("/api/leaves/requests/", body, format="json")

    def test_hr_is_notified_of_new_request_and_employee_of_decision(self):
        r = self.apply_leave()
        self.assertEqual(r.status_code, 201, r.content)
        self.assertTrue(Notification.objects.filter(user=self.hr_user, kind="LEAVE", title="New leave request").exists())
        self.assertFalse(Notification.objects.filter(user=self.emp.user, title="New leave request").exists())
        rid = r.json()["id"]
        client_for(self.hr_user).post(f"/api/leaves/requests/{rid}/approve/", {"remarks": "ok"}, format="json")
        self.assertTrue(Notification.objects.filter(user=self.emp.user, title="Leave request approved").exists())

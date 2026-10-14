import { useState } from "react";
import { Link } from "react-router-dom";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, PageHeader, Spinner, Stat, Table, fmtMoney, fmtTime, useFetch, useToast } from "../components/ui";
import { DonutChart, MiniCalendar } from "../components/widgets";

// Check-in / check-out box (also used on the Attendance page)
export function CheckInCard({ onChange }) {
  const toast = useToast();
  const { data, reload } = useFetch("/attendance/today/");
  const [busy, setBusy] = useState(false);

  const act = async (path) => {
    setBusy(true);
    try {
      await api.post(`/attendance/${path}/`);
      toast(path === "check-in" ? "Checked in" : "Checked out");
      reload();
      onChange?.();
    } catch (e) {
      toast(errMsg(e), "err");
    } finally {
      setBusy(false);
    }
  };

  const checkedIn = data?.check_in;
  const checkedOut = data?.check_out;

  return (
    <Card title="Today's attendance">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="text-sm text-slate-600">
          <div>Check-in: <b>{fmtTime(checkedIn)}</b> &nbsp; Check-out: <b>{fmtTime(checkedOut)}</b></div>
          {checkedOut && <div className="mt-1">Hours worked: <b>{data.working_hours}</b> ({data.status.replace("_", " ")})</div>}
        </div>
        <div className="flex gap-2">
          <Btn variant="success" disabled={busy || !!checkedIn} onClick={() => act("check-in")}>Check in</Btn>
          <Btn variant="danger" disabled={busy || !checkedIn || !!checkedOut} onClick={() => act("check-out")}>Check out</Btn>
        </div>
      </div>
    </Card>
  );
}

function AdminDashboard() {
  const { data, loading } = useFetch("/reports/dashboard/admin/");
  const { data: pending } = useFetch("/leaves/requests/", { status: "PENDING", page_size: 5 });

  if (loading || !data) return <Spinner />;
  const { employees, attendance_today: today, leaves, payroll } = data;

  const departments = employees.by_department.map((d) => ({ label: d.department__name || "Unassigned", value: d.count }));

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Total employees" value={employees.total} sub={`${employees.active} active / ${employees.inactive} inactive`} />
        <Stat label="Checked in today" value={today.checked_in} tone="green" sub={today.is_workday ? `${today.not_checked_in} not yet in` : "Weekend"} />
        <Stat label="On leave today" value={today.on_leave} tone="amber" />
        <Stat label="Pending leave requests" value={leaves.pending} tone="red" sub={`${leaves.approved_this_month} approved this month`} />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Employees by department">
          {departments.length === 0 ? (
            <p className="text-sm text-slate-400">No data</p>
          ) : (
            <DonutChart data={departments} centerValue={employees.active} centerLabel="Employees" />
          )}
        </Card>

        <Card title="Latest payroll">
          {payroll ? (
            <div className="space-y-3 text-sm text-slate-600">
              <div className="text-lg font-semibold text-slate-800">{payroll.period}</div>
              <div className="flex justify-between"><span>Employees paid</span><b>{payroll.employees_paid}</b></div>
              <div className="flex justify-between"><span>Total net payout</span><b>INR {fmtMoney(payroll.total_net)}</b></div>
              <div className="flex justify-between"><span>Credited (simulated)</span><b>{payroll.credited} / {payroll.employees_paid}</b></div>
            </div>
          ) : (
            <p className="text-sm text-slate-400">No payroll generated yet.</p>
          )}
        </Card>

        <Card title="Calendar">
          <MiniCalendar />
        </Card>
      </div>

      <Card title="Application status" actions={<Link to="/leaves" className="text-sm font-medium text-brand hover:underline">View all</Link>}>
        <Table
          rows={pending?.results || []}
          empty="No pending leave applications."
          columns={[
            { key: "employee_code", label: "Code" },
            { key: "employee_name", label: "Name" },
            { key: "leave_type_name", label: "Leave" },
            { key: "start_date", label: "From" },
            { key: "end_date", label: "To" },
            { key: "days", label: "Days" },
            { key: "reason", label: "Reason" },
            { label: "Status", render: (r) => <Badge v={r.status} /> },
          ]}
        />
      </Card>
    </div>
  );
}

function EmployeeDashboard() {
  const { data, loading, reload } = useFetch("/reports/dashboard/employee/");
  if (loading || !data) return <Spinner />;
  const month = data.month;

  return (
    <div className="space-y-6">
      <CheckInCard onChange={reload} />

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Stat label="Working days (this month)" value={month.working_days} />
        <Stat label="Present days" value={month.present_days} tone="green" sub={`${month.half_days} half day(s)`} />
        <Stat label="Pending leave requests" value={data.pending_leaves} tone="amber" />
        <Stat label="Last net salary" value={data.last_payroll ? fmtMoney(data.last_payroll.net) : "-"} sub={data.last_payroll?.period} tone="slate" />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Leave balances" className="lg:col-span-2">
          <Table
            rows={data.leave_balances}
            columns={[
              { key: "leave_type_name", label: "Leave type" },
              { key: "allocated", label: "Allocated" },
              { key: "used", label: "Used" },
              { label: "Remaining", render: (r) => <b>{r.remaining}</b> },
            ]}
          />
        </Card>
        <Card title="Calendar">
          <MiniCalendar />
        </Card>
      </div>
    </div>
  );
}

export default function Dashboard() {
  const { user, isStaff } = useAuth();
  const noProfile = !isStaff && !user.has_employee; // logged in, but not linked to an employee record
  return (
    <>
      <PageHeader title={`Welcome, ${user.first_name || user.username}`} sub={isStaff ? "Organisation overview" : "Your workspace"} />
      {isStaff && user.has_employee && <div className="mb-6"><CheckInCard /></div>}
      {noProfile ? (
        <Card>
          <p className="text-sm text-slate-600">
            Your login is not linked to an employee profile yet, so there is nothing to show here.
            Please ask HR or the Admin to add you under Employees.
          </p>
        </Card>
      ) : isStaff ? (
        <AdminDashboard />
      ) : (
        <EmployeeDashboard />
      )}
    </>
  );
}

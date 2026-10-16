import { useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, MONTHS, Modal, PageHeader, Pager, Select, Stat, Table, Tabs, Textarea, fmtTime, usePaged, useFetch, useToast } from "../components/ui";
import { CheckInCard } from "./Dashboard";

const now = new Date();

// columns that come from the shift calculation
const shiftCols = [
  { key: "shift_name", label: "Shift" },
  { label: "Late", render: (r) => (r.late_minutes ? <span className="text-amber-600">{r.late_minutes} min</span> : "-") },
  { label: "Early exit", render: (r) => (r.early_exit_minutes ? <span className="text-rose-600">{r.early_exit_minutes} min</span> : "-") },
  { label: "Overtime", render: (r) => (Number(r.overtime_hours) ? `${r.overtime_hours} h` : "-") },
];

function MyAttendance() {
  const [m, setM] = useState({ year: now.getFullYear(), month: now.getMonth() + 1 });
  const { data: sum, reload: reloadSum } = useFetch("/attendance/my-summary/", m);
  const first = `${m.year}-${String(m.month).padStart(2, "0")}-01`;
  const last = new Date(m.year, m.month, 0).toISOString().slice(0, 10);
  const { rows, count, page, setPage, reload } = usePaged("/attendance/", { date__gte: first, date__lte: last, ordering: "-date" });
  return (
    <div className="space-y-6">
      <CheckInCard onChange={() => { reload(); reloadSum(); }} />
      <div className="flex gap-3">
        <Select className="w-40" value={m.month} onChange={(e) => setM({ ...m, month: +e.target.value })}>{MONTHS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</Select>
        <Input className="w-28" type="number" value={m.year} onChange={(e) => setM({ ...m, year: +e.target.value })} />
      </div>
      {sum && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-5">
          <Stat label="Working days" value={sum.working_days} /><Stat label="Present" value={sum.present_days} tone="green" /><Stat label="Half days" value={sum.half_days} tone="amber" />
          <Stat label="Leave (paid / LOP)" value={`${sum.paid_leave_days} / ${sum.lop_leave_days}`} tone="slate" /><Stat label="Absent / LOP" value={sum.absent_days} tone="red" sub={`${sum.total_hours} hrs worked`} />
        </div>
      )}
      {sum && (
        <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat label="Holidays (weekdays)" value={sum.holidays} tone="slate" sub="not counted as working days" />
          <Stat label="Late check-ins" value={sum.late_days} tone="amber" />
          <Stat label="Overtime" value={`${sum.overtime_hours} h`} tone="green" />
        </div>
      )}
      <Card title="Attendance history">
        <Table rows={rows} columns={[{ key: "date", label: "Date" }, { label: "Check-in", render: (r) => fmtTime(r.check_in) }, { label: "Check-out", render: (r) => fmtTime(r.check_out) }, { key: "working_hours", label: "Hours" }, ...shiftCols, { label: "Status", render: (r) => <Badge v={r.status} /> }, { label: "", render: (r) => r.is_overridden && <span className="text-xs text-slate-400" title={r.override_note}>corrected by HR</span> }]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
    </div>
  );
}

function OverrideModal({ depts, onClose, onSaved, preset }) {
  const toast = useToast();
  const { data: emps } = useFetch("/employees/", { is_active: true, page_size: 200 });
  const { data: shifts } = useFetch("/shifts/");
  const [f, setF] = useState({ employee: preset?.employee ?? "", date: preset?.date ?? "", shift: "", status: "PRESENT", check_in: "", check_out: "", note: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const save = async (e) => {
    e.preventDefault();
    const body = { employee: +f.employee, date: f.date, status: f.status, note: f.note };
    if (f.shift) body.shift = +f.shift;
    if (f.check_in && f.check_out) { body.check_in = new Date(`${f.date}T${f.check_in}`).toISOString(); body.check_out = new Date(`${f.date}T${f.check_out}`).toISOString(); }
    try { await api.post("/attendance/override/", body); toast("Attendance corrected"); onSaved(); onClose(); } catch (er) { toast(errMsg(er), "err"); }
  };
  return (
    <Modal title="Attendance override" onClose={onClose}>
      <form onSubmit={save} className="space-y-4">
        <Field label="Employee"><Select required value={f.employee} onChange={set("employee")}><option value="">Select...</option>{(emps?.results || []).map((x) => <option key={x.id} value={x.id}>{x.employee_code} - {x.first_name} {x.last_name}</option>)}</Select></Field>
        <Field label="Date"><Input type="date" required value={f.date} onChange={set("date")} /></Field>
        <Field label="Shift (optional)" hint="Leave empty to use the employee's shift for that date"><Select value={f.shift} onChange={set("shift")}><option value="">Employee's shift</option>{(shifts || []).filter((x) => x.is_active).map((x) => <option key={x.id} value={x.id}>{x.name}</option>)}</Select></Field>
        <Field label="Status"><Select value={f.status} onChange={set("status")}><option value="PRESENT">Present</option><option value="HALF_DAY">Half day</option><option value="ABSENT">Absent</option></Select></Field>
        <div className="grid grid-cols-2 gap-3"><Field label="Check-in (optional)"><Input type="time" value={f.check_in} onChange={set("check_in")} /></Field><Field label="Check-out (optional)"><Input type="time" value={f.check_out} onChange={set("check_out")} /></Field></div>
        <Field label="Reason for correction" hint="Required - recorded in the audit log"><Textarea required value={f.note} onChange={set("note")} /></Field>
        <div className="flex justify-end gap-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save correction</Btn></div>
      </form>
    </Modal>
  );
}

function AllAttendance() {
  const [q, setQ] = useState({ date__gte: "", date__lte: "", employee__department: "", status: "", ordering: "-date" });
  const { rows, count, page, setPage, reload } = usePaged("/attendance/", q);
  const { data: depts } = useFetch("/employees/departments/");
  const [ov, setOv] = useState(false);
  return (
    <Card title="All employees" actions={<Btn small onClick={() => setOv(true)}>Override / correct</Btn>}>
      <div className="mb-4 flex flex-wrap gap-3">
        <Field label="From"><Input type="date" value={q.date__gte} onChange={(e) => setQ({ ...q, date__gte: e.target.value })} /></Field>
        <Field label="To"><Input type="date" value={q.date__lte} onChange={(e) => setQ({ ...q, date__lte: e.target.value })} /></Field>
        <Field label="Department"><Select value={q.employee__department} onChange={(e) => setQ({ ...q, employee__department: e.target.value })}><option value="">All</option>{(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</Select></Field>
        <Field label="Status"><Select value={q.status} onChange={(e) => setQ({ ...q, status: e.target.value })}><option value="">All</option><option value="PRESENT">Present</option><option value="HALF_DAY">Half day</option><option value="ABSENT">Absent</option></Select></Field>
      </div>
      <Table rows={rows} columns={[{ key: "date", label: "Date" }, { key: "employee_code", label: "Code" }, { key: "employee_name", label: "Employee" }, { key: "department", label: "Department" },
        { label: "In", render: (r) => fmtTime(r.check_in) }, { label: "Out", render: (r) => fmtTime(r.check_out) }, { key: "working_hours", label: "Hours" }, ...shiftCols, { label: "Status", render: (r) => <Badge v={r.status} /> },
        { label: "", render: (r) => r.is_overridden && <span className="text-xs text-amber-600" title={r.override_note}>overridden</span> }]} />
      <Pager page={page} setPage={setPage} count={count} />
      {ov && <OverrideModal onClose={() => setOv(false)} onSaved={reload} />}
    </Card>
  );
}

function MonthlySummary() {
  const [m, setM] = useState({ year: now.getFullYear(), month: now.getMonth() + 1 });
  const { data } = useFetch("/attendance/summary/", m);
  return (
    <Card title="Monthly attendance summary">
      <div className="mb-4 flex gap-3">
        <Select className="w-40" value={m.month} onChange={(e) => setM({ ...m, month: +e.target.value })}>{MONTHS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</Select>
        <Input className="w-28" type="number" value={m.year} onChange={(e) => setM({ ...m, year: +e.target.value })} />
      </div>
      <Table rows={data || []} columns={[{ key: "employee_code", label: "Code" }, { key: "employee_name", label: "Employee" }, { key: "working_days", label: "Working days" }, { key: "holidays", label: "Holidays" }, { key: "present_days", label: "Present" }, { key: "half_days", label: "Half" },
        { key: "paid_leave_days", label: "Paid leave" }, { key: "absent_days", label: "Absent / LOP" }, { key: "late_days", label: "Late days" }, { key: "overtime_hours", label: "Overtime h" }, { key: "total_hours", label: "Hours" }]} />
    </Card>
  );
}

export default function Attendance() {
  const { isStaff, user } = useAuth();
  const tabs = [...(user.has_employee ? [{ key: "mine", label: "My attendance" }] : []), ...(isStaff ? [{ key: "all", label: "All attendance" }, { key: "summary", label: "Monthly summary" }] : [])];
  const [tab, setTab] = useState(tabs[0]?.key);
  return (
    <>
      <PageHeader title="Attendance" sub="Check-in, check-out and daily tracking" />
      {tabs.length > 1 && <Tabs tabs={tabs} value={tab} onChange={setTab} />}
      {tab === "mine" && <MyAttendance />}{tab === "all" && <AllAttendance />}{tab === "summary" && <MonthlySummary />}
    </>
  );
}

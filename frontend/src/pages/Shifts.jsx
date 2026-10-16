import { useState } from "react";
import api, { download, errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, Modal, PageHeader, Pager, Select, Spinner, Stat, Table, Tabs, fmtHM, todayStr, usePaged, useFetch, useToast } from "../components/ui";

const timing = (s) => `${fmtHM(s.start_time)} - ${fmtHM(s.end_time)}${s.is_overnight ? " (+1 day)" : ""}`;
const isRunning = (a) => !a.end_date || a.end_date >= todayStr();

/* ---------- employee: my shift ---------- */
function MyShift() {
  const { data, loading } = useFetch("/shifts/my-shift/");
  const history = usePaged("/shifts/assignments/", { ordering: "-start_date" });
  if (loading || !data) return <Spinner />;
  const s = data.shift;
  const source = { employee: "Assigned to you", department: "Assigned to your department", default: "Company default" }[data.source];

  return (
    <div className="space-y-6">
      <Card title="Your shift today">
        <div className="grid gap-4 sm:grid-cols-4">
          <Stat label={s.name} value={timing(s)} sub={source} />
          <Stat label="Shift type" value={s.kind_label} tone="slate" />
          <Stat label="Grace period" value={`${s.grace_minutes} min`} tone="amber" sub="before check-in counts as late" />
          <Stat label="Expected hours" value={s.work_hours} tone="green" sub={`${s.scheduled_hours} h window, overtime after`} />
        </div>
      </Card>
      <Card title="Shift history">
        <Table
          rows={history.rows}
          empty="No shift assigned yet. You follow the company default shift."
          columns={[
            { key: "shift_name", label: "Shift" },
            { label: "Assigned as", render: (r) => (r.employee ? "Personal" : `Department (${r.department_name})`) },
            { key: "start_date", label: "From" },
            { label: "To", render: (r) => r.end_date || "Ongoing" },
            { label: "Status", render: (r) => <Badge v={isRunning(r) ? "ACTIVE" : "ENDED"}>{isRunning(r) ? "Active" : "Ended"}</Badge> },
          ]}
        />
        <Pager page={history.page} setPage={history.setPage} count={history.count} />
      </Card>
    </div>
  );
}

/* ---------- staff: shift definitions ---------- */
const blankShift = { name: "", kind: "GENERAL", start_time: "09:00", end_time: "18:00", grace_minutes: 10, work_hours: 8, is_active: true };

function ShiftForm({ initial, onClose, onSaved }) {
  const toast = useToast();
  const [f, setF] = useState(initial ? { ...initial, start_time: fmtHM(initial.start_time), end_time: fmtHM(initial.end_time) } : blankShift);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    try {
      const body = { name: f.name, kind: f.kind, start_time: f.start_time, end_time: f.end_time, grace_minutes: f.grace_minutes, work_hours: f.work_hours, is_active: f.is_active };
      if (initial) await api.patch(`/shifts/${initial.id}/`, body); else await api.post("/shifts/", body);
      toast("Shift saved");
      onSaved();
      onClose();
    } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Modal title={initial ? "Edit shift" : "Add shift"} onClose={onClose}>
      <form onSubmit={save} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Name"><Input required maxLength={60} value={f.name} onChange={set("name")} /></Field>
        <Field label="Type">
          <Select value={f.kind} onChange={set("kind")}>
            <option value="GENERAL">General</option><option value="NIGHT">Night</option><option value="FLEXIBLE">Flexible</option><option value="REMOTE">Remote</option>
          </Select>
        </Field>
        <Field label="Start time"><Input type="time" required value={f.start_time} onChange={set("start_time")} /></Field>
        <Field label="End time" hint="Earlier than start = ends next morning"><Input type="time" required value={f.end_time} onChange={set("end_time")} /></Field>
        <Field label="Grace period (minutes)"><Input type="number" min="0" max="120" required value={f.grace_minutes} onChange={set("grace_minutes")} /></Field>
        <Field label="Expected working hours" hint="Less than half of this is a half day"><Input type="number" min="1" max="16" step="0.5" required value={f.work_hours} onChange={set("work_hours")} /></Field>
        {f.kind === "FLEXIBLE" && <p className="text-xs text-slate-500 sm:col-span-2">Flexible shifts never mark late check-in or early check-out; only the hours worked count.</p>}
        {initial && (
          <label className="flex items-center gap-2 text-sm text-slate-600 sm:col-span-2">
            <input type="checkbox" checked={f.is_active} onChange={(e) => setF({ ...f, is_active: e.target.checked })} /> Active
          </label>
        )}
        <div className="flex justify-end gap-2 sm:col-span-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save</Btn></div>
      </form>
    </Modal>
  );
}

function ShiftList() {
  const toast = useToast();
  const { data, loading, reload } = useFetch("/shifts/");
  const [form, setForm] = useState(null);

  const remove = async (s) => {
    if (!confirm(`Delete shift "${s.name}"?`)) return;
    try { await api.delete(`/shifts/${s.id}/`); reload(); } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Card title="Work shifts" actions={<Btn onClick={() => setForm({})}>Add shift</Btn>}>
      {loading ? <Spinner /> : (
        <Table
          rows={data || []}
          columns={[
            { key: "name", label: "Name" },
            { label: "Type", render: (r) => <Badge v={r.kind}>{r.kind_label}</Badge> },
            { label: "Timing", render: timing },
            { label: "Grace", render: (r) => `${r.grace_minutes} min` },
            { key: "work_hours", label: "Hours/day" },
            { label: "Status", render: (r) => <Badge v={r.is_active ? "ACTIVE" : "INACTIVE"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
            { label: "", render: (r) => <div className="flex gap-2"><Btn small variant="secondary" onClick={() => setForm(r)}>Edit</Btn><Btn small variant="danger" onClick={() => remove(r)}>Delete</Btn></div> },
          ]}
        />
      )}
      {form && <ShiftForm initial={form.id ? form : null} onClose={() => setForm(null)} onSaved={reload} />}
    </Card>
  );
}

/* ---------- staff: assignments + history ---------- */
function AssignForm({ shifts, onClose, onSaved }) {
  const toast = useToast();
  const { data: emps } = useFetch("/employees/", { is_active: true, page_size: 200 });
  const { data: depts } = useFetch("/employees/departments/");
  const [f, setF] = useState({ shift: "", target: "employee", employee: "", department: "", start_date: todayStr(), end_date: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    try {
      const body = { shift: f.shift, start_date: f.start_date, end_date: f.end_date || null };
      if (f.target === "employee") body.employee = f.employee; else body.department = f.department;
      await api.post("/shifts/assignments/", body);
      toast("Shift assigned");
      onSaved();
      onClose();
    } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Modal title="Assign shift" onClose={onClose}>
      <form onSubmit={save} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Shift">
          <Select required value={f.shift} onChange={set("shift")}>
            <option value="">Select...</option>
            {shifts.filter((s) => s.is_active).map((s) => <option key={s.id} value={s.id}>{s.name} ({timing(s)})</option>)}
          </Select>
        </Field>
        <Field label="Assign to">
          <Select value={f.target} onChange={set("target")}><option value="employee">One employee</option><option value="department">Whole department</option></Select>
        </Field>
        {f.target === "employee" ? (
          <Field label="Employee">
            <Select required value={f.employee} onChange={set("employee")}>
              <option value="">Select...</option>
              {(emps?.results || []).map((e) => <option key={e.id} value={e.id}>{e.employee_code} - {e.first_name} {e.last_name}</option>)}
            </Select>
          </Field>
        ) : (
          <Field label="Department">
            <Select required value={f.department} onChange={set("department")}>
              <option value="">Select...</option>
              {(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </Select>
          </Field>
        )}
        <Field label="Starts on" hint="A running assignment ends the day before"><Input type="date" required value={f.start_date} onChange={set("start_date")} /></Field>
        <Field label="Ends on (optional)"><Input type="date" value={f.end_date} onChange={set("end_date")} /></Field>
        <p className="text-xs text-slate-500 sm:col-span-2">A personal assignment overrides the department shift. Past assignments stay in the history.</p>
        <div className="flex justify-end gap-2 sm:col-span-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Assign</Btn></div>
      </form>
    </Modal>
  );
}

function Assignments() {
  const toast = useToast();
  const { data: shifts } = useFetch("/shifts/");
  const [shift, setShift] = useState("");
  const { rows, count, page, setPage, loading, reload } = usePaged("/shifts/assignments/", { shift });
  const [open, setOpen] = useState(false);

  const end = async (a) => {
    if (!confirm("End this assignment today?")) return;
    try { await api.post(`/shifts/assignments/${a.id}/end/`); reload(); } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Card
      title="Assignments & history"
      actions={
        <div className="flex gap-2">
          <Select value={shift} onChange={(e) => setShift(e.target.value)}>
            <option value="">All shifts</option>
            {(shifts || []).map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
          </Select>
          <Btn onClick={() => setOpen(true)}>Assign shift</Btn>
        </div>
      }
    >
      {loading ? <Spinner /> : (
        <Table
          rows={rows}
          empty="No assignments yet. Everyone follows the General Shift."
          columns={[
            { label: "Assigned to", render: (r) => (r.employee ? `${r.employee_code} - ${r.employee_name}` : `Department: ${r.department_name}`) },
            { key: "shift_name", label: "Shift" },
            { key: "start_date", label: "From" },
            { label: "To", render: (r) => r.end_date || "Ongoing" },
            { key: "assigned_by_name", label: "By" },
            { label: "Status", render: (r) => <Badge v={isRunning(r) ? "ACTIVE" : "ENDED"}>{isRunning(r) ? "Active" : "Ended"}</Badge> },
            { label: "", render: (r) => (isRunning(r) && !r.end_date ? <Btn small variant="secondary" onClick={() => end(r)}>End</Btn> : null) },
          ]}
        />
      )}
      <Pager page={page} setPage={setPage} count={count} />
      {open && <AssignForm shifts={shifts || []} onClose={() => setOpen(false)} onSaved={reload} />}
    </Card>
  );
}

/* ---------- staff: shift-wise attendance report ---------- */
function ShiftReport() {
  const { data: shifts } = useFetch("/shifts/");
  const { data: depts } = useFetch("/employees/departments/");
  const monthStart = todayStr().slice(0, 8) + "01";
  const [f, setF] = useState({ date_from: monthStart, date_to: todayStr(), shift: "", department: "" });
  const params = Object.fromEntries(Object.entries(f).filter(([, v]) => v));
  const { data, loading } = useFetch("/reports/shift-attendance/", params);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const rows = data?.rows || [];
  // column positions in the report: 8 = late minutes, 9 = early exit minutes, 10 = overtime hours
  const late = rows.filter((r) => Number(r[8]) > 0).length;
  const early = rows.filter((r) => Number(r[9]) > 0).length;
  const overtime = rows.reduce((sum, r) => sum + Number(r[10] || 0), 0);
  const columns = (data?.columns || []).map((label, i) => ({ label, render: (r) => r[i] }));

  return (
    <div className="space-y-6">
      <Card
        title="Shift-wise attendance"
        actions={
          <div className="flex gap-2">
            <Btn small variant="secondary" onClick={() => download("/reports/shift-attendance/", "shift_attendance.csv", { ...params, format: "csv" })}>CSV</Btn>
            <Btn small variant="secondary" onClick={() => download("/reports/shift-attendance/", "shift_attendance.pdf", { ...params, format: "pdf" })}>PDF</Btn>
          </div>
        }
      >
        <div className="mb-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Field label="From"><Input type="date" value={f.date_from} onChange={set("date_from")} /></Field>
          <Field label="To"><Input type="date" value={f.date_to} onChange={set("date_to")} /></Field>
          <Field label="Shift"><Select value={f.shift} onChange={set("shift")}><option value="">All shifts</option>{(shifts || []).map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}</Select></Field>
          <Field label="Department"><Select value={f.department} onChange={set("department")}><option value="">All departments</option>{(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</Select></Field>
        </div>
        <div className="mb-4 grid grid-cols-2 gap-4 lg:grid-cols-4">
          <Stat label="Records" value={rows.length} /><Stat label="Late check-ins" value={late} tone="amber" /><Stat label="Early check-outs" value={early} tone="red" /><Stat label="Overtime hours" value={overtime.toFixed(2)} tone="green" />
        </div>
        {loading ? <Spinner /> : <Table rows={rows} columns={columns} empty="No attendance in this range." />}
      </Card>
      <p className="text-xs text-slate-400">Corrections are made on the Attendance page (admin override), where a different shift can be picked for a day.</p>
    </div>
  );
}

export default function Shifts() {
  const { isStaff, user } = useAuth();
  const tabs = [
    ...(user.has_employee ? [{ key: "mine", label: "My shift" }] : []),
    ...(isStaff ? [{ key: "shifts", label: "Shifts" }, { key: "assign", label: "Assignments" }, { key: "report", label: "Shift report" }] : []),
  ];
  const [tab, setTab] = useState(tabs[0]?.key);

  return (
    <>
      <PageHeader title="Shifts & schedules" sub="Late check-in, early check-out and overtime are calculated from the shift" />
      {tabs.length === 0 ? <Card><p className="text-sm text-slate-600">Your login is not linked to an employee profile, so there is no shift to show.</p></Card> : (
        <>
          <Tabs tabs={tabs} value={tab} onChange={setTab} />
          {tab === "mine" && <MyShift />}
          {tab === "shifts" && <ShiftList />}
          {tab === "assign" && <Assignments />}
          {tab === "report" && <ShiftReport />}
        </>
      )}
    </>
  );
}

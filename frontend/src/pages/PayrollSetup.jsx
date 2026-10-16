import { useEffect, useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, MONTHS, Modal, Pager, Select, Spinner, Table, fmtMoney, lastMonth, todayStr, usePaged, useFetch, useToast } from "../components/ui";

// amount of one component: fixed value, or a percentage of the basic pay
const amountOf = (item, basic) => (item.calc_type === "PERCENT_OF_BASIC" ? (basic * Number(item.value)) / 100 : Number(item.value));

function summarize(items) {
  const basic = Number(items.find((i) => i.code === "BASIC")?.value || 0);
  const earnings = items.filter((i) => i.kind === "EARNING").reduce((s, i) => s + amountOf(i, basic), 0);
  const deductions = items.filter((i) => i.kind === "DEDUCTION").reduce((s, i) => s + amountOf(i, basic), 0);
  return { basic, earnings, deductions, net: earnings - deductions };
}

/* ---------- pay slip breakdown (used by both employee and staff tables) ---------- */
export function Breakdown({ row, onClose }) {
  // payrolls generated before the advanced module have no lines, so rebuild them from the flat columns
  const lines = row.lines?.length ? row.lines : [
    { name: "Basic", kind: "EARNING", amount: row.basic }, { name: "House Rent Allowance", kind: "EARNING", amount: row.hra },
    { name: "Other Allowances", kind: "EARNING", amount: row.allowances }, { name: "Provident Fund", kind: "DEDUCTION", amount: row.pf_deduction },
    { name: "Tax / TDS", kind: "DEDUCTION", amount: row.tax_deduction },
  ];
  const earn = lines.filter((l) => l.kind === "EARNING");
  const ded = [{ name: `Loss of pay (${row.lop_days} day${Number(row.lop_days) === 1 ? "" : "s"})`, amount: row.lop_deduction }, ...lines.filter((l) => l.kind === "DEDUCTION")];
  const adj = Number(row.adjustment);
  if (adj > 0) earn.push({ name: `Adjustment${row.adjustment_note ? ` - ${row.adjustment_note}` : ""}`, amount: adj });
  if (adj < 0) ded.push({ name: `Adjustment${row.adjustment_note ? ` - ${row.adjustment_note}` : ""}`, amount: -adj });
  const total = (list) => list.reduce((s, l) => s + Number(l.amount), 0);

  const Side = ({ title, list }) => (
    <div>
      <h4 className="mb-2 text-xs font-semibold uppercase text-slate-500">{title}</h4>
      <ul className="space-y-1.5 text-sm">
        {list.map((l, i) => <li key={i} className="flex justify-between gap-3"><span className="text-slate-600">{l.name}</span><span>{fmtMoney(l.amount)}</span></li>)}
      </ul>
      <div className="mt-2 flex justify-between border-t border-slate-200 pt-2 text-sm font-semibold"><span>Total</span><span>{fmtMoney(total(list))}</span></div>
    </div>
  );

  return (
    <Modal title={`Salary breakdown - ${MONTHS[row.month - 1]} ${row.year}`} onClose={onClose} wide>
      <div className="mb-4 flex flex-wrap gap-x-6 gap-y-1 text-xs text-slate-500">
        <span>Working days: <b>{row.working_days}</b></span><span>Present: <b>{row.present_days}</b></span>
        <span>Paid leave: <b>{row.paid_leave_days}</b></span><span>LOP: <b>{row.lop_days}</b></span><span>Overtime: <b>{row.overtime_hours} h</b></span>
      </div>
      <div className="grid gap-8 sm:grid-cols-2"><Side title="Earnings" list={earn} /><Side title="Deductions" list={ded} /></div>
      <div className="mt-6 flex justify-between rounded-lg bg-slate-100 px-4 py-3 text-sm"><span className="font-semibold text-slate-700">Net salary</span><span className="text-lg font-semibold text-slate-800">INR {fmtMoney(row.net_salary)}</span></div>
    </Modal>
  );
}

/* ---------- salary structure view + revision ---------- */
function StructureTable({ items }) {
  const s = summarize(items);
  return (
    <>
      <Table
        rows={items}
        columns={[
          { key: "name", label: "Component" },
          { label: "Type", render: (r) => <Badge v={r.kind} /> },
          { label: "Value", className: "text-right", render: (r) => (r.calc_type === "PERCENT_OF_BASIC" ? `${Number(r.value)}% of basic` : fmtMoney(r.value)) },
          { label: "Monthly amount", className: "text-right", render: (r) => fmtMoney(amountOf(r, s.basic)) },
        ]}
      />
      <div className="mt-3 flex flex-wrap justify-end gap-6 text-sm text-slate-600">
        <span>Gross <b>{fmtMoney(s.earnings)}</b></span><span>Deductions <b>{fmtMoney(s.deductions)}</b></span><span>Net before LOP <b>{fmtMoney(s.net)}</b></span>
      </div>
    </>
  );
}

function ReviseModal({ employee, current, onClose, onSaved }) {
  const toast = useToast();
  const { data: comps } = useFetch("/payroll/components/", { is_active: true, is_variable: false });
  const [items, setItems] = useState((current?.items || []).map((i) => ({ component: i.component, value: Number(i.value) })));
  const [f, setF] = useState({ effective_from: todayStr(), reason: "" });
  const byId = Object.fromEntries((comps || []).map((c) => [c.id, c]));

  const preview = summarize(items.filter((i) => byId[i.component]).map((i) => ({ ...byId[i.component], value: i.value })));
  const change = (idx, patch) => setItems(items.map((it, i) => (i === idx ? { ...it, ...patch } : it)));
  const unused = (comps || []).filter((c) => !items.some((i) => i.component === c.id));

  const save = async (e) => {
    e.preventDefault();
    try {
      await api.post("/payroll/structures/", { employee: employee.id, ...f, new_items: items.map((i) => ({ component: i.component, value: i.value })) });
      toast("Salary revised");
      onSaved();
      onClose();
    } catch (er) { toast(errMsg(er), "err"); }
  };

  if (!comps) return <Modal title="Revise salary" onClose={onClose}><Spinner /></Modal>;
  return (
    <Modal title={`Revise salary - ${employee.first_name} ${employee.last_name}`} onClose={onClose} wide>
      <form onSubmit={save} className="space-y-4">
        <div className="grid gap-4 sm:grid-cols-2">
          <Field label="Effective from" hint="Applies to payroll of this month onwards"><Input type="date" required value={f.effective_from} onChange={(e) => setF({ ...f, effective_from: e.target.value })} /></Field>
          <Field label="Reason"><Input required maxLength={255} placeholder="e.g. Annual appraisal" value={f.reason} onChange={(e) => setF({ ...f, reason: e.target.value })} /></Field>
        </div>
        <div className="space-y-2">
          {items.map((it, idx) => {
            const c = byId[it.component];
            return (
              <div key={it.component} className="flex items-center gap-2">
                <span className="w-48 truncate text-sm text-slate-700">{c?.name || "Inactive component"}</span>
                <Input className="w-36" type="number" min="0" step="0.01" required value={it.value} onChange={(e) => change(idx, { value: e.target.value })} />
                <span className="text-xs text-slate-400">{c?.calc_type === "PERCENT_OF_BASIC" ? "% of basic" : "per month"}</span>
                {c && <Badge v={c.kind} />}
                <button type="button" onClick={() => setItems(items.filter((_, i) => i !== idx))} className="ml-auto text-lg text-slate-400 hover:text-rose-500">&times;</button>
              </div>
            );
          })}
        </div>
        {unused.length > 0 && (
          <Select value="" onChange={(e) => e.target.value && setItems([...items, { component: Number(e.target.value), value: 0 }])} className="max-w-xs">
            <option value="">+ Add component...</option>
            {unused.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
          </Select>
        )}
        <div className="flex flex-wrap justify-end gap-6 rounded-lg bg-slate-100 px-4 py-3 text-sm">
          <span>Gross <b>{fmtMoney(preview.earnings)}</b></span><span>Deductions <b>{fmtMoney(preview.deductions)}</b></span><span>Net <b>{fmtMoney(preview.net)}</b></span>
        </div>
        <p className="text-xs text-slate-500">The old structure stays in the history. Payslips already generated are not changed.</p>
        <div className="flex justify-end gap-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save revision</Btn></div>
      </form>
    </Modal>
  );
}

function StructureHistory({ employeeId }) {
  const { rows, count, page, setPage, loading } = usePaged("/payroll/structures/", { employee: employeeId });
  if (loading) return <Spinner />;
  return (
    <>
      <Table
        rows={rows}
        empty="No revisions yet."
        columns={[
          { key: "effective_from", label: "Effective from" },
          { key: "reason", label: "Reason" },
          { key: "created_by_name", label: "Revised by" },
          { label: "Basic", className: "text-right", render: (r) => fmtMoney(r.items.find((i) => i.code === "BASIC")?.value) },
          { label: "Gross", className: "text-right", render: (r) => fmtMoney(summarize(r.items).earnings) },
        ]}
      />
      <Pager page={page} setPage={setPage} count={count} />
    </>
  );
}

// employee: own salary structure
export function MySalary() {
  const { data, loading } = useFetch("/payroll/structures/current/");
  if (loading || !data) return <Spinner />;
  return (
    <div className="space-y-6">
      <Card title={`Current salary structure (from ${data.effective_from})`}><StructureTable items={data.items} /></Card>
      {data.id && <Card title="Revision history"><StructureHistory employeeId={data.employee} /></Card>}
    </div>
  );
}

// staff: pick an employee, see the structure, admin can revise it
export function SalaryStructures() {
  const { isAdmin } = useAuth();
  const { data: emps } = useFetch("/employees/", { is_active: true, page_size: 200 });
  const [empId, setEmpId] = useState("");
  const { data: current, loading, reload } = useFetch("/payroll/structures/current/", { employee: empId }, !!empId);
  const [revise, setRevise] = useState(false);
  const [version, setVersion] = useState(0);
  const employee = (emps?.results || []).find((e) => String(e.id) === String(empId));

  return (
    <div className="space-y-6">
      <Card title="Salary structure" actions={isAdmin && employee ? <Btn onClick={() => setRevise(true)}>Revise salary</Btn> : null}>
        <Field label="Employee">
          <Select className="max-w-sm" value={empId} onChange={(e) => setEmpId(e.target.value)}>
            <option value="">Select employee...</option>
            {(emps?.results || []).map((e) => <option key={e.id} value={e.id}>{e.employee_code} - {e.first_name} {e.last_name}</option>)}
          </Select>
        </Field>
        {empId && (loading || !current ? <Spinner /> : (
          <div className="mt-4">
            {!current.id && <p className="mb-3 rounded-lg bg-amber-50 px-3 py-2 text-xs text-amber-700">No structure yet, showing the salary fields of the employee profile. Revising salary creates the first structure.</p>}
            <p className="mb-2 text-xs text-slate-500">Effective from {current.effective_from}{current.reason ? ` - ${current.reason}` : ""}</p>
            <StructureTable items={current.items} />
          </div>
        ))}
      </Card>
      {empId && current?.id && <Card title="Revision history" key={version}><StructureHistory employeeId={empId} /></Card>}
      {revise && employee && current && <ReviseModal employee={employee} current={current} onClose={() => setRevise(false)} onSaved={() => { reload(); setVersion(version + 1); }} />}
    </div>
  );
}

/* ---------- salary components (admin edits, HR reads) ---------- */
const blankComp = { name: "", code: "", kind: "EARNING", calc_type: "FIXED", is_variable: false, display_order: 50, is_active: true };

function ComponentForm({ initial, onClose, onSaved }) {
  const toast = useToast();
  const [f, setF] = useState(initial || blankComp);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const locked = !!initial?.is_system; // payroll rules depend on these, so only name/order can change

  const save = async (e) => {
    e.preventDefault();
    try {
      const body = { name: f.name, code: f.code, kind: f.kind, calc_type: f.is_variable ? "FIXED" : f.calc_type, is_variable: f.is_variable, display_order: f.display_order, is_active: f.is_active };
      if (initial) await api.patch(`/payroll/components/${initial.id}/`, body); else await api.post("/payroll/components/", body);
      toast("Component saved");
      onSaved();
      onClose();
    } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Modal title={initial ? "Edit component" : "Add component"} onClose={onClose}>
      <form onSubmit={save} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Name"><Input required maxLength={60} value={f.name} onChange={set("name")} /></Field>
        <Field label="Code"><Input required maxLength={20} disabled={locked} value={f.code} onChange={set("code")} placeholder="e.g. CONVEYANCE" /></Field>
        <Field label="Type"><Select disabled={locked} value={f.kind} onChange={(e) => setF({ ...f, kind: e.target.value, is_variable: e.target.value === "EARNING" && f.is_variable })}><option value="EARNING">Earning</option><option value="DEDUCTION">Deduction</option></Select></Field>
        <Field label="Calculation"><Select disabled={locked || f.is_variable} value={f.is_variable ? "FIXED" : f.calc_type} onChange={set("calc_type")}><option value="FIXED">Fixed amount</option><option value="PERCENT_OF_BASIC">% of basic</option></Select></Field>
        <Field label="Display order"><Input type="number" min="0" value={f.display_order} onChange={set("display_order")} /></Field>
        <div className="flex flex-col justify-end gap-2 text-sm text-slate-600">
          {f.kind === "EARNING" && <label className="flex items-center gap-2"><input type="checkbox" disabled={locked} checked={f.is_variable} onChange={(e) => setF({ ...f, is_variable: e.target.checked })} /> Variable (bonus / incentive, entered monthly)</label>}
          {initial && <label className="flex items-center gap-2"><input type="checkbox" disabled={locked} checked={f.is_active} onChange={(e) => setF({ ...f, is_active: e.target.checked })} /> Active</label>}
        </div>
        <div className="flex justify-end gap-2 sm:col-span-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save</Btn></div>
      </form>
    </Modal>
  );
}

export function SalaryComponents() {
  const { isAdmin } = useAuth();
  const toast = useToast();
  const { data, loading, reload } = useFetch("/payroll/components/");
  const [form, setForm] = useState(null);

  const remove = async (c) => {
    if (!confirm(`Delete "${c.name}"?`)) return;
    try { await api.delete(`/payroll/components/${c.id}/`); reload(); } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Card title="Salary components" actions={isAdmin ? <Btn onClick={() => setForm({})}>Add component</Btn> : null}>
      {loading ? <Spinner /> : (
        <Table
          rows={data || []}
          columns={[
            { key: "name", label: "Name" }, { key: "code", label: "Code" },
            { label: "Type", render: (r) => <Badge v={r.kind} /> },
            { label: "Calculation", render: (r) => (r.is_variable ? "Variable, entered monthly" : r.calc_type === "PERCENT_OF_BASIC" ? "% of basic" : "Fixed amount") },
            { label: "Status", render: (r) => <Badge v={r.is_active ? "ACTIVE" : "INACTIVE"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
            { label: "", render: (r) => isAdmin && (
              <div className="flex gap-2"><Btn small variant="secondary" onClick={() => setForm(r)}>Edit</Btn>{!r.is_system && <Btn small variant="danger" onClick={() => remove(r)}>Delete</Btn>}</div>
            ) },
          ]}
        />
      )}
      {!isAdmin && <p className="mt-3 text-xs text-slate-400">Only Admin can change components.</p>}
      {form && <ComponentForm initial={form.id ? form : null} onClose={() => setForm(null)} onSaved={reload} />}
    </Card>
  );
}

/* ---------- variable pay (bonus / incentives per month) ---------- */
function VariableForm({ period, onClose, onSaved }) {
  const toast = useToast();
  const { data: emps } = useFetch("/employees/", { is_active: true, page_size: 200 });
  const { data: comps } = useFetch("/payroll/components/", { is_variable: true, is_active: true });
  const [f, setF] = useState({ employee: "", component: "", amount: "", note: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  useEffect(() => { if (comps?.length && !f.component) setF((x) => ({ ...x, component: comps[0].id })); }, [comps]); // eslint-disable-line

  const save = async (e) => {
    e.preventDefault();
    try { await api.post("/payroll/variable-pay/", { ...f, year: period.year, month: period.month }); toast("Saved"); onSaved(); onClose(); }
    catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Modal title={`Add variable pay - ${MONTHS[period.month - 1]} ${period.year}`} onClose={onClose}>
      {comps && comps.length === 0 ? <p className="text-sm text-slate-600">No variable component exists. Ask the Admin to add one under Components.</p> : (
        <form onSubmit={save} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
          <Field label="Employee"><Select required value={f.employee} onChange={set("employee")}><option value="">Select...</option>{(emps?.results || []).map((e) => <option key={e.id} value={e.id}>{e.employee_code} - {e.first_name} {e.last_name}</option>)}</Select></Field>
          <Field label="Component"><Select required value={f.component} onChange={set("component")}>{(comps || []).map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}</Select></Field>
          <Field label="Amount"><Input type="number" min="0.01" step="0.01" required value={f.amount} onChange={set("amount")} /></Field>
          <Field label="Note"><Input maxLength={255} value={f.note} onChange={set("note")} /></Field>
          <p className="text-xs text-slate-500 sm:col-span-2">Entered before the month's payroll is generated. Saving the same employee and component again replaces the amount.</p>
          <div className="flex justify-end gap-2 sm:col-span-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save</Btn></div>
        </form>
      )}
    </Modal>
  );
}

export function VariablePay() {
  const toast = useToast();
  const [period, setPeriod] = useState(lastMonth());
  const { rows, count, page, setPage, loading, reload } = usePaged("/payroll/variable-pay/", period);
  const [open, setOpen] = useState(false);

  const remove = async (r) => {
    if (!confirm("Remove this entry?")) return;
    try { await api.delete(`/payroll/variable-pay/${r.id}/`); reload(); } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Card
      title="Variable pay (bonus / incentives)"
      actions={
        <div className="flex gap-2">
          <Select className="w-36" value={period.month} onChange={(e) => setPeriod({ ...period, month: +e.target.value })}>{MONTHS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</Select>
          <Input className="w-24" type="number" value={period.year} onChange={(e) => setPeriod({ ...period, year: +e.target.value })} />
          <Btn onClick={() => setOpen(true)}>Add</Btn>
        </div>
      }
    >
      {loading ? <Spinner /> : (
        <Table
          rows={rows}
          empty="No variable pay entered for this month."
          columns={[
            { key: "employee_code", label: "Code" }, { key: "employee_name", label: "Employee" }, { key: "component_name", label: "Component" },
            { label: "Amount", className: "text-right", render: (r) => fmtMoney(r.amount) }, { key: "note", label: "Note" },
            { label: "", render: (r) => <Btn small variant="danger" onClick={() => remove(r)}>Remove</Btn> },
          ]}
        />
      )}
      <Pager page={page} setPage={setPage} count={count} />
      {open && <VariableForm period={period} onClose={() => setOpen(false)} onSaved={reload} />}
    </Card>
  );
}
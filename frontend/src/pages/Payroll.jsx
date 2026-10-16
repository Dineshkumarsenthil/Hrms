import { useState } from "react";
import api, { download, errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, MONTHS, Modal, PageHeader, Pager, Select, Table, Tabs, fmtMoney, lastMonth, usePaged, useToast } from "../components/ui";
import { Breakdown, MySalary, SalaryComponents, SalaryStructures, VariablePay } from "./PayrollSetup";

const periodCol = { label: "Period", render: (r) => `${MONTHS[r.month - 1].slice(0, 3)} ${r.year}` };
const slipBtn = (r) => <Btn small variant="secondary" onClick={() => download(`/payroll/${r.id}/slip/`, `salary_slip_${r.employee_code}_${r.year}-${String(r.month).padStart(2, "0")}.pdf`)}>Slip PDF</Btn>;

function MySlips() {
  const { rows, count, page, setPage } = usePaged("/payroll/", { ordering: "-year" });
  const [view, setView] = useState(null);
  return (
    <Card title="My payroll history & salary slips">
      {view && <Breakdown row={view} onClose={() => setView(null)} />}
      <Table rows={rows} empty="No salary slips yet." columns={[periodCol, { label: "Gross", className: "text-right", render: (r) => fmtMoney(r.gross_salary) }, { label: "LOP days", key: "lop_days" },
        { label: "Deductions", className: "text-right", render: (r) => fmtMoney(+r.lop_deduction + +r.pf_deduction + +r.tax_deduction + +r.other_deductions) }, { label: "Net salary", className: "text-right font-semibold", render: (r) => fmtMoney(r.net_salary) },
        { label: "Status", render: (r) => <Badge v={r.status} /> }, { label: "", render: (r) => <div className="flex gap-1.5"><Btn small variant="secondary" onClick={() => setView(r)}>Breakdown</Btn>{r.has_slip && slipBtn(r)}</div> }]} />
      <Pager page={page} setPage={setPage} count={count} />
    </Card>
  );
}

function Manage() {
  const { isAdmin } = useAuth();
  const toast = useToast();
  const lm = lastMonth();
  const [gen, setGen] = useState(lm);
  const [q, setQ] = useState({ year: lm.year, month: lm.month, status: "" });
  const { rows, count, page, setPage, reload } = usePaged("/payroll/", q);
  const [view, setView] = useState(null);
  const [adj, setAdj] = useState(null);
  const [adjForm, setAdjForm] = useState({ amount: "", note: "" });

  const run = async (fn, okMsg) => { try { const r = await fn(); toast(typeof okMsg === "function" ? okMsg(r.data) : okMsg); reload(); } catch (e) { toast(errMsg(e), "err"); } };
  const generate = () => run(() => api.post("/payroll/generate/", gen), (d) => `${d.generated} payroll(s) generated, ${d.skipped.length} skipped`);
  const creditAll = () => confirm("Simulate salary credit for all generated payrolls of this month?") && run(() => api.post("/payroll/credit-all/", gen), (d) => `${d.credited} salaries credited (simulated)`);
  const unlock = (r) => { const reason = prompt("Reason for unlocking this payroll?"); if (reason) run(() => api.post(`/payroll/${r.id}/unlock/`, { reason }), "Payroll unlocked"); };

  return (
    <div className="space-y-6">
      <Card title="Process payroll">
        <div className="flex flex-wrap items-end gap-3">
          <Field label="Month"><Select value={gen.month} onChange={(e) => setGen({ ...gen, month: +e.target.value })}>{MONTHS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</Select></Field>
          <Field label="Year"><Input className="w-28" type="number" value={gen.year} onChange={(e) => setGen({ ...gen, year: +e.target.value })} /></Field>
          <Btn onClick={generate}>Generate payroll</Btn>
          <Btn variant="success" onClick={creditAll}>Credit all (simulated)</Btn>
        </div>
        <p className="mt-3 text-xs text-slate-400">Salary = gross (from the salary structure) + variable pay + overtime - LOP - deductions. Working days exclude weekends and holidays. Payroll locks automatically after generation; only Admin can unlock to adjust.</p>
      </Card>
      <Card title="Payroll records">
        <div className="mb-4 flex flex-wrap gap-3">
          <Select className="w-40" value={q.month} onChange={(e) => setQ({ ...q, month: e.target.value })}><option value="">All months</option>{MONTHS.map((n, i) => <option key={n} value={i + 1}>{n}</option>)}</Select>
          <Input className="w-28" type="number" placeholder="Year" value={q.year} onChange={(e) => setQ({ ...q, year: e.target.value })} />
          <Select className="w-40" value={q.status} onChange={(e) => setQ({ ...q, status: e.target.value })}><option value="">All status</option><option value="GENERATED">Generated</option><option value="CREDITED">Credited</option></Select>
        </div>
        <Table rows={rows} columns={[periodCol, { key: "employee_code", label: "Code" }, { key: "employee_name", label: "Employee" }, { key: "lop_days", label: "LOP" },
          { label: "Gross", className: "text-right", render: (r) => fmtMoney(r.gross_salary) }, { label: "Adjust.", className: "text-right", render: (r) => fmtMoney(r.adjustment) },
          { label: "Net", className: "text-right font-semibold", render: (r) => fmtMoney(r.net_salary) }, { label: "Status", render: (r) => <div className="flex items-center gap-1"><Badge v={r.status} />{r.locked && <span title="Locked">&#128274;</span>}</div> },
          { label: "", render: (r) => (
            <div className="flex flex-wrap gap-1.5">
              <Btn small variant="secondary" onClick={() => setView(r)}>Breakdown</Btn>
              {r.has_slip && slipBtn(r)}
              {r.status === "GENERATED" && r.locked && <Btn small variant="success" onClick={() => run(() => api.post(`/payroll/${r.id}/credit/`), "Salary credited (simulated)")}>Credit</Btn>}
              {isAdmin && r.status === "GENERATED" && r.locked && <Btn small variant="secondary" onClick={() => unlock(r)}>Unlock</Btn>}
              {isAdmin && r.status === "GENERATED" && !r.locked && <><Btn small onClick={() => { setAdj(r); setAdjForm({ amount: r.adjustment, note: r.adjustment_note }); }}>Adjust</Btn><Btn small variant="secondary" onClick={() => run(() => api.post(`/payroll/${r.id}/lock/`), "Payroll locked")}>Lock</Btn></>}
            </div>) }]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
      {view && <Breakdown row={view} onClose={() => setView(null)} />}
      {adj && (
        <Modal title={`Manual adjustment - ${adj.employee_name}`} onClose={() => setAdj(null)}>
          <div className="space-y-4">
            <Field label="Amount (+ bonus / - deduction)"><Input type="number" step="0.01" value={adjForm.amount} onChange={(e) => setAdjForm({ ...adjForm, amount: e.target.value })} /></Field>
            <Field label="Note"><Input value={adjForm.note} onChange={(e) => setAdjForm({ ...adjForm, note: e.target.value })} /></Field>
            <div className="flex justify-end gap-2"><Btn variant="secondary" onClick={() => setAdj(null)}>Cancel</Btn>
              <Btn onClick={() => run(() => api.post(`/payroll/${adj.id}/adjust/`, adjForm), "Adjustment saved - remember to lock the payroll again").then(() => setAdj(null))}>Save adjustment</Btn></div>
          </div>
        </Modal>
      )}
    </div>
  );
}

export default function Payroll() {
  const { isStaff, user } = useAuth();
  const tabs = [
    ...(isStaff ? [{ key: "manage", label: "Payroll management" }, { key: "structure", label: "Salary structures" }, { key: "variable", label: "Variable pay" }, { key: "components", label: "Components" }] : []),
    ...(user.has_employee ? [{ key: "mine", label: "My salary slips" }, { key: "mysalary", label: "My salary structure" }] : []),
  ];
  const [tab, setTab] = useState(tabs[0]?.key);
  return (
    <>
      <PageHeader title={isStaff ? "Payroll" : "Salary Slips"} sub="Monthly salary processing and PDF salary slips" />
      {tabs.length > 1 && <Tabs tabs={tabs} value={tab} onChange={setTab} />}
      {tab === "manage" && <Manage />}{tab === "mine" && <MySlips />}
      {tab === "structure" && <SalaryStructures />}{tab === "variable" && <VariablePay />}{tab === "components" && <SalaryComponents />}{tab === "mysalary" && <MySalary />}
    </>
  );
}

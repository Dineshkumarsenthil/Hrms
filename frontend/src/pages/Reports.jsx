import { useState } from "react";
import api, { download, errMsg } from "../api";
import { Btn, Card, Field, Input, PageHeader, Select, Table, useFetch, useToast } from "../components/ui";

const TYPES = { attendance: "Attendance report", leaves: "Leave report", payroll: "Payroll summary" };

export default function Reports() {
  const toast = useToast();
  const { data: depts } = useFetch("/employees/departments/");
  const [f, setF] = useState({ type: "attendance", date_from: "", date_to: "", department: "", status: "" });
  const [res, setRes] = useState(null);
  const params = () => Object.fromEntries(Object.entries({ date_from: f.date_from, date_to: f.date_to, department: f.department, status: f.type === "leaves" ? f.status : "" }).filter(([, v]) => v));
  const preview = async () => { try { const { data } = await api.get(`/reports/${f.type}/`, { params: params() }); setRes(data); } catch (e) { toast(errMsg(e), "err"); } };
  const exportAs = async (format) => { try { await download(`/reports/${f.type}/`, `${f.type}_report.${format}`, { ...params(), format }); } catch (e) { toast("Export failed", "err"); } };
  const cols = res ? res.columns.map((c, i) => ({ label: c, render: (r) => r[i] })) : [];

  return (
    <>
      <PageHeader title="Reports & Analytics" sub="Filter by date and department, then preview or export" />
      <Card>
        <div className="flex flex-wrap items-end gap-3">
          <Field label="Report"><Select value={f.type} onChange={(e) => { setF({ ...f, type: e.target.value }); setRes(null); }}>{Object.entries(TYPES).map(([k, v]) => <option key={k} value={k}>{v}</option>)}</Select></Field>
          <Field label="From"><Input type="date" value={f.date_from} onChange={(e) => setF({ ...f, date_from: e.target.value })} /></Field>
          <Field label="To"><Input type="date" value={f.date_to} onChange={(e) => setF({ ...f, date_to: e.target.value })} /></Field>
          <Field label="Department"><Select value={f.department} onChange={(e) => setF({ ...f, department: e.target.value })}><option value="">All</option>{(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</Select></Field>
          {f.type === "leaves" && <Field label="Status"><Select value={f.status} onChange={(e) => setF({ ...f, status: e.target.value })}><option value="">All</option><option value="PENDING">Pending</option><option value="APPROVED">Approved</option><option value="REJECTED">Rejected</option></Select></Field>}
          <Btn onClick={preview}>Preview</Btn>
          <Btn variant="secondary" onClick={() => exportAs("csv")}>Export CSV</Btn>
          <Btn variant="secondary" onClick={() => exportAs("pdf")}>Export PDF</Btn>
        </div>
      </Card>
      {res && <Card title={`${res.title} (${res.rows.length} rows)`} className="mt-6"><Table columns={cols} rows={res.rows.map((r, i) => Object.assign([...r], { id: i }))} /></Card>}
    </>
  );
}

import { useEffect, useState } from "react";
import api, { download, errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, Modal, PageHeader, Pager, Select, Table, fmtMoney, fmtDateTime, usePaged, useFetch, useToast } from "../components/ui";

const blank = { first_name: "", last_name: "", email: "", role: "EMPLOYEE", department: "", designation: "", phone: "", joining_date: "", basic_salary: "", hra: "", allowances: "", pf_percent: "12", tax_deduction: "0" };

function EmployeeForm({ initial, depts, onClose, onSaved }) {
  const { isAdmin } = useAuth();
  const toast = useToast();
  const [f, setF] = useState(initial ? { ...blank, ...initial, department: initial.department ?? "" } : blank);
  const [created, setCreated] = useState(null);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    try {
      const body = { ...f, department: f.department || null };
      if (initial) { await api.patch(`/employees/${initial.id}/`, body); toast("Employee updated"); onSaved(); onClose(); }
      else { const { data } = await api.post("/employees/", body); setCreated(data); toast("Employee created"); onSaved(); }
    } catch (er) { toast(errMsg(er), "err"); }
  };

  if (created) return (
    <Modal title="Employee created" onClose={onClose}>
      <p className="text-sm">Account created for <b>{created.first_name} {created.last_name}</b> ({created.employee_code}). An onboarding email has been sent.</p>
      <div className="my-4 rounded-lg bg-slate-100 p-4 text-sm">Username: <b>{created.username}</b><br />Temporary password: <b className="font-mono">{created.temporary_password}</b></div>
      <p className="text-xs text-slate-500">Shown only once. The employee should change it after first login.</p>
      <div className="mt-4 text-right"><Btn onClick={onClose}>Done</Btn></div>
    </Modal>
  );

  return (
    <Modal title={initial ? "Edit employee" : "Add employee"} onClose={onClose} wide>
      <form onSubmit={save} className="grid grid-cols-2 gap-4">
        <Field label="First name"><Input required value={f.first_name} onChange={set("first_name")} /></Field>
        <Field label="Last name"><Input value={f.last_name} onChange={set("last_name")} /></Field>
        <Field label="Email"><Input type="email" required value={f.email} onChange={set("email")} /></Field>
        <Field label="Phone"><Input value={f.phone} onChange={set("phone")} /></Field>
        <Field label="Department"><Select required value={f.department} onChange={set("department")}><option value="">Select...</option>{depts.map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</Select></Field>
        <Field label="Designation"><Input required value={f.designation} onChange={set("designation")} /></Field>
        <Field label="Joining date"><Input type="date" required value={f.joining_date} onChange={set("joining_date")} /></Field>
        <Field label="Role"><Select value={f.role} onChange={set("role")} disabled={!isAdmin}><option value="EMPLOYEE">Employee</option><option value="HR">HR</option><option value="ADMIN">Admin</option></Select></Field>
        <Field label="Basic salary"><Input type="number" min="0" step="0.01" required value={f.basic_salary} onChange={set("basic_salary")} /></Field>
        <Field label="HRA"><Input type="number" min="0" step="0.01" required value={f.hra} onChange={set("hra")} /></Field>
        <Field label="Allowances"><Input type="number" min="0" step="0.01" required value={f.allowances} onChange={set("allowances")} /></Field>
        <Field label="PF % of basic"><Input type="number" min="0" max="100" step="0.01" value={f.pf_percent} onChange={set("pf_percent")} /></Field>
        <Field label="Tax deduction (monthly)"><Input type="number" min="0" step="0.01" value={f.tax_deduction} onChange={set("tax_deduction")} /></Field>
        <div className="col-span-2 flex justify-end gap-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Save</Btn></div>
      </form>
    </Modal>
  );
}

function Documents({ emp, onClose }) {
  const toast = useToast();
  const { data, reload } = useFetch(`/employees/${emp.id}/documents/`);
  const [title, setTitle] = useState("");
  const [file, setFile] = useState(null);

  const upload = async (e) => {
    e.preventDefault();
    const fd = new FormData(); fd.append("title", title); fd.append("file", file);
    try { await api.post(`/employees/${emp.id}/documents/`, fd); toast("Uploaded"); setTitle(""); setFile(null); e.target.reset(); reload(); }
    catch (er) { toast(errMsg(er), "err"); }
  };
  const del = async (id) => { if (!confirm("Delete this document?")) return; try { await api.delete(`/employees/documents/${id}/`); reload(); } catch (er) { toast(errMsg(er), "err"); } };

  return (
    <Modal title={`Documents - ${emp.first_name} ${emp.last_name}`} onClose={onClose} wide>
      <form onSubmit={upload} className="mb-5 flex flex-wrap items-end gap-3">
        <Field label="Title"><Input required value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. ID proof" /></Field>
        <Field label="File" hint="PDF, PNG, JPG, DOC(X) - max 5 MB"><input required type="file" accept=".pdf,.png,.jpg,.jpeg,.doc,.docx" onChange={(e) => setFile(e.target.files[0])} className="text-sm" /></Field>
        <Btn>Upload</Btn>
      </form>
      <Table rows={data || []} empty="No documents yet." columns={[{ key: "title", label: "Title" }, { key: "original_name", label: "File" }, { label: "Uploaded", render: (r) => fmtDateTime(r.uploaded_at) },
        { label: "", render: (r) => <div className="flex gap-2"><Btn small variant="secondary" onClick={() => download(`/employees/documents/${r.id}/download/`, r.original_name || "document")}>Download</Btn><Btn small variant="danger" onClick={() => del(r.id)}>Delete</Btn></div> }]} />
    </Modal>
  );
}

export default function Employees() {
  const toast = useToast();
  const [q, setQ] = useState({ search: "", department: "", is_active: "" });
  const { rows, count, page, setPage, loading, reload } = usePaged("/employees/", q);
  const { data: depts, reload: reloadDepts } = useFetch("/employees/departments/");
  const [modal, setModal] = useState(null); // {type, emp}
  const [newDept, setNewDept] = useState("");

  const toggle = async (e) => {
    if (!confirm(`${e.is_active ? "Deactivate" : "Activate"} ${e.first_name}?`)) return;
    try { await api.post(`/employees/${e.id}/${e.is_active ? "deactivate" : "activate"}/`); toast(e.is_active ? "Employee deactivated" : "Employee activated"); reload(); }
    catch (er) { toast(errMsg(er), "err"); }
  };
  const addDept = async () => { if (!newDept.trim()) return; try { await api.post("/employees/departments/", { name: newDept.trim() }); setNewDept(""); toast("Department added"); reloadDepts(); } catch (er) { toast(errMsg(er), "err"); } };

  return (
    <>
      <PageHeader title="Employees" sub="Onboard, update and deactivate employees"><Btn onClick={() => setModal({ type: "form" })}>+ Add employee</Btn></PageHeader>
      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input className="max-w-xs" placeholder="Search name, code, email..." value={q.search} onChange={(e) => setQ({ ...q, search: e.target.value })} />
          <Select className="max-w-[200px]" value={q.department} onChange={(e) => setQ({ ...q, department: e.target.value })}><option value="">All departments</option>{(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}</Select>
          <Select className="max-w-[160px]" value={q.is_active} onChange={(e) => setQ({ ...q, is_active: e.target.value })}><option value="">All status</option><option value="true">Active</option><option value="false">Inactive</option></Select>
          <div className="ml-auto flex gap-2"><Input className="w-40" placeholder="New department" value={newDept} onChange={(e) => setNewDept(e.target.value)} /><Btn variant="secondary" onClick={addDept}>Add</Btn></div>
        </div>
        <Table rows={rows} empty={loading ? "Loading..." : undefined} columns={[
          { key: "employee_code", label: "Code" },
          { label: "Name", render: (r) => <div><div className="font-medium">{r.first_name} {r.last_name}</div><div className="text-xs text-slate-400">{r.email}</div></div> },
          { key: "department_name", label: "Department" }, { key: "designation", label: "Designation" }, { key: "joining_date", label: "Joined" },
          { label: "Gross", className: "text-right", render: (r) => fmtMoney(r.gross_salary) },
          { label: "Role", render: (r) => <Badge v={r.role} /> },
          { label: "Status", render: (r) => <Badge v={r.is_active ? "APPROVED" : "REJECTED"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
          { label: "", render: (r) => <div className="flex gap-1.5"><Btn small variant="secondary" onClick={() => setModal({ type: "form", emp: r })}>Edit</Btn><Btn small variant="secondary" onClick={() => setModal({ type: "docs", emp: r })}>Docs</Btn><Btn small variant={r.is_active ? "danger" : "success"} onClick={() => toggle(r)}>{r.is_active ? "Deactivate" : "Activate"}</Btn></div> },
        ]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
      {modal?.type === "form" && <EmployeeForm initial={modal.emp} depts={depts || []} onClose={() => setModal(null)} onSaved={reload} />}
      {modal?.type === "docs" && <Documents emp={modal.emp} onClose={() => setModal(null)} />}
    </>
  );
}

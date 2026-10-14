import { useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, Modal, PageHeader, Pager, Select, Stat, Table, Tabs, Textarea, usePaged, useFetch, useToast } from "../components/ui";

const today = new Date().toLocaleDateString("en-CA"); // today as YYYY-MM-DD in local time

function ApplyModal({ types, onClose, onSaved }) {
  const toast = useToast();
  const [f, setF] = useState({ leave_type: "", start_date: today, end_date: today, reason: "" });
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });
  const save = async (e) => {
    e.preventDefault();
    try { const { data } = await api.post("/leaves/requests/", { ...f, leave_type: +f.leave_type }); toast(data.lop_days > 0 ? `Submitted - ${data.lop_days} day(s) will be Loss of Pay` : "Leave request submitted"); onSaved(); onClose(); }
    catch (er) { toast(errMsg(er), "err"); }
  };
  return (
    <Modal title="Apply for leave" onClose={onClose}>
      <form onSubmit={save} className="space-y-4">
        <Field label="Leave type"><Select required value={f.leave_type} onChange={set("leave_type")}><option value="">Select...</option>{types.map((t) => <option key={t.id} value={t.id}>{t.name}{t.is_paid ? "" : " (unpaid)"}</option>)}</Select></Field>
        <div className="grid grid-cols-2 gap-3">
          <Field label="From"><Input type="date" required min={today} value={f.start_date} onChange={set("start_date")} /></Field>
          <Field label="To"><Input type="date" required min={f.start_date} value={f.end_date} onChange={set("end_date")} /></Field>
        </div>
        <Field label="Reason"><Textarea required maxLength={500} value={f.reason} onChange={set("reason")} /></Field>
        <p className="text-xs text-slate-400">Weekends are excluded. Days beyond your balance are treated as Loss of Pay.</p>
        <div className="flex justify-end gap-2"><Btn type="button" variant="secondary" onClick={onClose}>Cancel</Btn><Btn>Submit</Btn></div>
      </form>
    </Modal>
  );
}

function MyLeaves() {
  const toast = useToast();
  const { data: types } = useFetch("/leaves/types/");
  const { data: bal, reload: reloadBal } = useFetch("/leaves/balances/");
  const { rows, count, page, setPage, reload } = usePaged("/leaves/requests/", {});
  const [open, setOpen] = useState(false);
  const cancel = async (id) => { if (!confirm("Cancel this request?")) return; try { await api.post(`/leaves/requests/${id}/cancel/`); toast("Request cancelled"); reload(); reloadBal(); } catch (e) { toast(errMsg(e), "err"); } };
  return (
    <div className="space-y-6">
      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">{(bal || []).filter((b) => b.allocated > 0).map((b) => <Stat key={b.id} label={b.leave_type_name} value={b.remaining} sub={`${b.used} used of ${b.allocated}`} tone="green" />)}</div>
      <Card title="Leave history" actions={<Btn small onClick={() => setOpen(true)}>+ Apply for leave</Btn>}>
        <Table rows={rows} columns={[{ key: "leave_type_name", label: "Type" }, { key: "start_date", label: "From" }, { key: "end_date", label: "To" }, { key: "days", label: "Days" }, { key: "lop_days", label: "LOP" },
          { key: "reason", label: "Reason" }, { label: "Status", render: (r) => <Badge v={r.status} /> }, { key: "remarks", label: "HR remarks" },
          { label: "", render: (r) => (r.status === "PENDING" || (r.status === "APPROVED" && r.start_date > today)) && <Btn small variant="secondary" onClick={() => cancel(r.id)}>Cancel</Btn> }]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
      {open && <ApplyModal types={types || []} onClose={() => setOpen(false)} onSaved={() => { reload(); reloadBal(); }} />}
    </div>
  );
}

function Manage() {
  const toast = useToast();
  const [q, setQ] = useState({ status: "PENDING" });
  const { rows, count, page, setPage, reload } = usePaged("/leaves/requests/", q);
  const [review, setReview] = useState(null); // {req, action}
  const [remarks, setRemarks] = useState("");
  const submit = async () => {
    try { await api.post(`/leaves/requests/${review.req.id}/${review.action}/`, { remarks }); toast(`Request ${review.action}d`); setReview(null); setRemarks(""); reload(); }
    catch (e) { toast(errMsg(e), "err"); }
  };
  return (
    <Card title="Leave requests">
      <div className="mb-4 w-48"><Select value={q.status} onChange={(e) => setQ({ status: e.target.value })}><option value="">All</option><option value="PENDING">Pending</option><option value="APPROVED">Approved</option><option value="REJECTED">Rejected</option><option value="CANCELLED">Cancelled</option></Select></div>
      <Table rows={rows} columns={[{ key: "employee_code", label: "Code" }, { key: "employee_name", label: "Employee" }, { key: "leave_type_name", label: "Type" }, { key: "start_date", label: "From" }, { key: "end_date", label: "To" },
        { key: "days", label: "Days" }, { key: "lop_days", label: "LOP" }, { key: "reason", label: "Reason" }, { label: "Status", render: (r) => <Badge v={r.status} /> },
        { label: "", render: (r) => r.status === "PENDING" && <div className="flex gap-1.5"><Btn small variant="success" onClick={() => setReview({ req: r, action: "approve" })}>Approve</Btn><Btn small variant="danger" onClick={() => setReview({ req: r, action: "reject" })}>Reject</Btn></div> }]} />
      <Pager page={page} setPage={setPage} count={count} />
      {review && (
        <Modal title={`${review.action === "approve" ? "Approve" : "Reject"} leave - ${review.req.employee_name}`} onClose={() => setReview(null)}>
          <p className="mb-3 text-sm text-slate-600">{review.req.leave_type_name}: {review.req.start_date} to {review.req.end_date} ({review.req.days} day(s))</p>
          <Field label="Remarks (optional)"><Textarea value={remarks} onChange={(e) => setRemarks(e.target.value)} /></Field>
          <div className="mt-4 flex justify-end gap-2"><Btn variant="secondary" onClick={() => setReview(null)}>Cancel</Btn><Btn variant={review.action === "approve" ? "success" : "danger"} onClick={submit}>Confirm</Btn></div>
        </Modal>
      )}
    </Card>
  );
}

export default function Leaves() {
  const { isStaff, user } = useAuth();
  const tabs = [...(user.has_employee ? [{ key: "mine", label: "My leave" }] : []), ...(isStaff ? [{ key: "manage", label: "Manage requests" }] : [])];
  const [tab, setTab] = useState(isStaff ? "manage" : tabs[0]?.key);
  return (
    <>
      <PageHeader title="Leave Management" sub="Apply, track and approve leave" />
      {tabs.length > 1 && <Tabs tabs={tabs} value={tab} onChange={setTab} />}
      {tab === "mine" && <MyLeaves />}{tab === "manage" && <Manage />}
    </>
  );
}

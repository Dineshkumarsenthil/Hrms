import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, PageHeader, Pager, Select, Spinner, Table, Tabs, Textarea, fmtAgo, fmtDateTime, usePaged, useFetch, useToast } from "../components/ui";

function Inbox() {
  const toast = useToast();
  const navigate = useNavigate();
  const [unreadOnly, setUnreadOnly] = useState("");
  const { rows, count, page, setPage, loading, reload } = usePaged("/notifications/", { is_read: unreadOnly });

  const run = async (fn) => { try { await fn(); reload(); } catch (e) { toast(errMsg(e), "err"); } };
  const open = async (n) => {
    if (!n.is_read) await api.post(`/notifications/${n.id}/mark-read/`).catch(() => {});
    if (n.link) navigate(n.link); else reload();
  };

  return (
    <Card
      title="Inbox"
      actions={
        <div className="flex items-center gap-2">
          <Select value={unreadOnly} onChange={(e) => setUnreadOnly(e.target.value)}>
            <option value="">All</option>
            <option value="false">Unread only</option>
          </Select>
          <Btn variant="secondary" onClick={() => run(() => api.post("/notifications/mark-all-read/"))}>Mark all read</Btn>
        </div>
      }
    >
      {loading ? <Spinner /> : rows.length === 0 ? (
        <p className="p-6 text-center text-sm text-slate-400">No notifications.</p>
      ) : (
        <ul className="divide-y divide-slate-100">
          {rows.map((n) => (
            <li key={n.id} className="flex flex-wrap items-start gap-3 py-3">
              <span className={`mt-2 h-2 w-2 shrink-0 rounded-full ${n.is_read ? "bg-slate-200" : "bg-brand"}`} />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <span className={`text-sm ${n.is_read ? "text-slate-700" : "font-semibold text-slate-800"}`}>{n.title}</span>
                  <Badge v={n.kind}>{n.kind_label}</Badge>
                  <span className="text-xs text-slate-400" title={fmtDateTime(n.created_at)}>{fmtAgo(n.created_at)}</span>
                </div>
                <p className="mt-0.5 text-sm text-slate-500">{n.message}</p>
              </div>
              <div className="flex gap-2">
                {n.link && <Btn small variant="secondary" onClick={() => open(n)}>Open</Btn>}
                {!n.is_read && <Btn small variant="secondary" onClick={() => run(() => api.post(`/notifications/${n.id}/mark-read/`))}>Mark read</Btn>}
                <Btn small variant="danger" onClick={() => run(() => api.delete(`/notifications/${n.id}/`))}>Delete</Btn>
              </div>
            </li>
          ))}
        </ul>
      )}
      <Pager page={page} setPage={setPage} count={count} />
    </Card>
  );
}

function Preferences() {
  const toast = useToast();
  const { data, loading, reload } = useFetch("/notifications/preferences/");

  const toggle = async (p) => {
    try { await api.put("/notifications/preferences/", [{ kind: p.kind, enabled: !p.enabled }]); reload(); }
    catch (e) { toast(errMsg(e), "err"); }
  };

  return (
    <Card title="Notification preferences">
      <p className="mb-4 text-sm text-slate-500">Choose which in-app notifications you want to receive. Emails are not affected.</p>
      {loading ? <Spinner /> : (
        <ul className="divide-y divide-slate-100">
          {(data || []).map((p) => (
            <li key={p.kind} className="flex items-center justify-between py-3">
              <span className="text-sm text-slate-700">{p.label}</span>
              <button
                role="switch"
                aria-checked={p.enabled}
                onClick={() => toggle(p)}
                className={`relative h-6 w-11 rounded-full transition ${p.enabled ? "bg-brand" : "bg-slate-300"}`}
              >
                <span className={`absolute top-0.5 h-5 w-5 rounded-full bg-white shadow transition-all ${p.enabled ? "left-5" : "left-0.5"}`} />
              </button>
            </li>
          ))}
        </ul>
      )}
    </Card>
  );
}

function Broadcasts() {
  const toast = useToast();
  const { data: depts } = useFetch("/employees/departments/");
  const history = usePaged("/notifications/broadcasts/");
  const [f, setF] = useState({ title: "", message: "", department: "" });
  const [busy, setBusy] = useState(false);

  const send = async (e) => {
    e.preventDefault();
    setBusy(true);
    try {
      const { data } = await api.post("/notifications/broadcasts/", { ...f, department: f.department || null });
      toast(`Sent to ${data.recipient_count} people`);
      setF({ title: "", message: "", department: "" });
      history.reload();
    } catch (er) { toast(errMsg(er), "err"); } finally { setBusy(false); }
  };

  return (
    <div className="grid gap-6 lg:grid-cols-5">
      <Card title="Send announcement" className="lg:col-span-2">
        <form onSubmit={send} className="space-y-4">
          <Field label="Send to">
            <Select value={f.department} onChange={(e) => setF({ ...f, department: e.target.value })}>
              <option value="">Whole organization</option>
              {(depts || []).map((d) => <option key={d.id} value={d.id}>{d.name}</option>)}
            </Select>
          </Field>
          <Field label="Title"><Input required maxLength={120} value={f.title} onChange={(e) => setF({ ...f, title: e.target.value })} /></Field>
          <Field label="Message"><Textarea required rows={4} maxLength={1000} value={f.message} onChange={(e) => setF({ ...f, message: e.target.value })} /></Field>
          <Btn disabled={busy}>Send</Btn>
        </form>
      </Card>
      <Card title="Sent announcements" className="lg:col-span-3">
        <Table
          rows={history.rows}
          empty="Nothing sent yet."
          columns={[
            { label: "When", render: (r) => fmtDateTime(r.created_at) },
            { key: "title", label: "Title" },
            { key: "department_name", label: "Audience" },
            { key: "recipient_count", label: "Delivered" },
            { key: "sent_by_name", label: "By" },
          ]}
        />
        <Pager page={history.page} setPage={history.setPage} count={history.count} />
      </Card>
    </div>
  );
}

export default function Notifications() {
  const { isAdmin } = useAuth();
  const [tab, setTab] = useState("inbox");
  const tabs = [{ key: "inbox", label: "Inbox" }, { key: "prefs", label: "Preferences" }, ...(isAdmin ? [{ key: "send", label: "Send announcement" }] : [])];

  return (
    <>
      <PageHeader title="Notifications" sub="Leave, payroll, attendance and announcements" />
      <Tabs tabs={tabs} value={tab} onChange={setTab} />
      {tab === "inbox" ? <Inbox /> : tab === "prefs" ? <Preferences /> : <Broadcasts />}
    </>
  );
}
import { useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, PageHeader, Pager, Select, Table, fmtDateTime, usePaged, useFetch, useToast } from "../components/ui";

export function AuditLogs() {
  const [q, setQ] = useState({ action: "", entity: "", created_at__date__gte: "", created_at__date__lte: "", search: "" });
  const { rows, count, page, setPage } = usePaged("/audit/", q);
  return (
    <>
      <PageHeader title="Audit Logs" sub="Read-only record of critical system actions" />
      <Card>
        <div className="mb-4 flex flex-wrap gap-3">
          <Input className="w-56" placeholder="Search user / action..." value={q.search} onChange={(e) => setQ({ ...q, search: e.target.value })} />
          <Input className="w-48" placeholder="Entity (e.g. Payroll)" value={q.entity} onChange={(e) => setQ({ ...q, entity: e.target.value })} />
          <Input type="date" value={q.created_at__date__gte} onChange={(e) => setQ({ ...q, created_at__date__gte: e.target.value })} />
          <Input type="date" value={q.created_at__date__lte} onChange={(e) => setQ({ ...q, created_at__date__lte: e.target.value })} />
        </div>
        <Table rows={rows} columns={[{ label: "Time", render: (r) => fmtDateTime(r.created_at) }, { key: "username", label: "User" }, { label: "Action", render: (r) => <span className="font-mono text-xs">{r.action}</span> },
          { key: "entity", label: "Entity" }, { key: "entity_id", label: "ID" }, { key: "ip_address", label: "IP" }, { label: "Details", render: (r) => <span className="text-xs text-slate-500">{Object.keys(r.details || {}).length ? JSON.stringify(r.details) : "-"}</span> }]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
    </>
  );
}

export function EmailLogs() {
  const [q, setQ] = useState({ status: "", template_code: "" });
  const { rows, count, page, setPage } = usePaged("/notifications/logs/", q);
  return (
    <>
      <PageHeader title="Email Logs" sub="Every notification email sent by the system" />
      <Card>
        <div className="mb-4 w-44"><Select value={q.status} onChange={(e) => setQ({ ...q, status: e.target.value })}><option value="">All status</option><option value="SENT">Sent</option><option value="FAILED">Failed</option></Select></div>
        <Table rows={rows} columns={[{ label: "Time", render: (r) => fmtDateTime(r.created_at) }, { key: "template_code", label: "Template" }, { key: "to_email", label: "To" }, { key: "subject", label: "Subject" }, { label: "Status", render: (r) => <Badge v={r.status} /> }]} />
        <Pager page={page} setPage={setPage} count={count} />
      </Card>
    </>
  );
}

export function Users() {
  const { user: me } = useAuth();
  const toast = useToast();
  const { rows, count, page, setPage, reload } = usePaged("/auth/users/", {});
  const { data: matrix } = useFetch("/auth/roles/");
  const patch = async (u, body) => { try { await api.patch(`/auth/users/${u.id}/`, body); toast("User updated"); reload(); } catch (e) { toast(errMsg(e), "err"); } };
  return (
    <>
      <PageHeader title="Users & Roles" sub="Role and permission management (Admin only)" />
      <div className="grid gap-6 lg:grid-cols-3">
        <Card title="Users" className="lg:col-span-2">
          <Table rows={rows} columns={[{ key: "username", label: "Username" }, { key: "email", label: "Email" },
            { label: "Role", render: (u) => <Select className="w-32" value={u.role} disabled={u.id === me.id} onChange={(e) => patch(u, { role: e.target.value })}><option value="ADMIN">Admin</option><option value="HR">HR</option><option value="EMPLOYEE">Employee</option></Select> },
            { label: "Active", render: (u) => <Btn small variant={u.is_active ? "success" : "danger"} disabled={u.id === me.id} onClick={() => patch(u, { is_active: !u.is_active })}>{u.is_active ? "Active" : "Disabled"}</Btn> }]} />
          <Pager page={page} setPage={setPage} count={count} />
        </Card>
        <Card title="Role permissions">
          {matrix && Object.entries(matrix).map(([role, perms]) => (
            <div key={role} className="mb-4"><Badge v={role} /><ul className="mt-2 list-disc pl-5 text-sm text-slate-600">{perms.map((p) => <li key={p}>{p}</li>)}</ul></div>
          ))}
        </Card>
      </div>
    </>
  );
}

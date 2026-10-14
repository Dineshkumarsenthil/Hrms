import { useState } from "react";
import api, { download, errMsg } from "../api";
import { Btn, Card, Field, Input, PageHeader, Spinner, Table, fmtDateTime, fmtMoney, useFetch, useToast } from "../components/ui";

export default function Profile() {
  const { data, loading } = useFetch("/employees/me/");
  const toast = useToast();
  const [pw, setPw] = useState({ old_password: "", new_password: "" });
  if (loading || !data) return <Spinner />;

  const changePw = async (e) => {
    e.preventDefault();
    try { await api.post("/auth/change-password/", pw); toast("Password updated"); setPw({ old_password: "", new_password: "" }); }
    catch (er) { toast(errMsg(er), "err"); }
  };
  const row = (k, v) => <div className="flex justify-between border-b border-slate-100 py-2 text-sm"><span className="text-slate-500">{k}</span><span className="font-medium">{v || "-"}</span></div>;

  return (
    <>
      <PageHeader title="My Profile" sub={`${data.employee_code} - ${data.designation}`} />
      <div className="grid gap-6 lg:grid-cols-2">
        <Card title="Employee details">
          {row("Name", `${data.first_name} ${data.last_name}`)}{row("Username", data.username)}{row("Email", data.email)}{row("Phone", data.phone)}
          {row("Department", data.department_name)}{row("Designation", data.designation)}{row("Joining date", data.joining_date)}
        </Card>
        <Card title="Salary structure (monthly)">
          {row("Basic", fmtMoney(data.basic_salary))}{row("HRA", fmtMoney(data.hra))}{row("Allowances", fmtMoney(data.allowances))}
          {row("Gross", fmtMoney(data.gross_salary))}{row("PF %", data.pf_percent)}{row("Tax deduction", fmtMoney(data.tax_deduction))}
        </Card>
        <Card title="My documents">
          <Table columns={[{ key: "title", label: "Title" }, { key: "original_name", label: "File" }, { label: "Uploaded", render: (r) => fmtDateTime(r.uploaded_at) },
            { label: "", render: (r) => <Btn small variant="secondary" onClick={() => download(`/employees/documents/${r.id}/download/`, r.original_name || "document")}>Download</Btn> }]} rows={data.documents} empty="No documents uploaded." />
        </Card>
        <Card title="Change password">
          <form onSubmit={changePw} className="space-y-3">
            <Field label="Current password"><Input type="password" required value={pw.old_password} onChange={(e) => setPw({ ...pw, old_password: e.target.value })} /></Field>
            <Field label="New password" hint="Min 8 characters, not too common"><Input type="password" required value={pw.new_password} onChange={(e) => setPw({ ...pw, new_password: e.target.value })} /></Field>
            <Btn>Update password</Btn>
          </form>
        </Card>
      </div>
    </>
  );
}

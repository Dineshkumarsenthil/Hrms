import { useState } from "react";
import api, { errMsg } from "../api";
import { useAuth } from "../auth";
import { Badge, Btn, Card, Field, Input, Modal, PageHeader, Select, Table, Tabs, Spinner, useFetch, useToast } from "../components/ui";
import { HolidayCalendar } from "../components/widgets";

const blank = { name: "", date: "", kind: "COMPANY", region: "", description: "", is_active: true };

function HolidayForm({ initial, onClose, onSaved }) {
  const toast = useToast();
  const [f, setF] = useState(initial || blank);
  const set = (k) => (e) => setF({ ...f, [k]: e.target.value });

  const save = async (e) => {
    e.preventDefault();
    try {
      if (initial) await api.patch(`/holidays/${initial.id}/`, f);
      else await api.post("/holidays/", f);
      toast(initial ? "Holiday updated" : "Holiday added");
      onSaved();
      onClose();
    } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Modal title={initial ? "Edit holiday" : "Add holiday"} onClose={onClose}>
      <form onSubmit={save} className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        <Field label="Name"><Input required maxLength={100} value={f.name} onChange={set("name")} /></Field>
        <Field label="Date"><Input type="date" required value={f.date} onChange={set("date")} /></Field>
        <Field label="Type" hint="Optional holidays are listed but do not remove a working day">
          <Select value={f.kind} onChange={set("kind")}>
            <option value="COMPANY">Company-wide</option>
            <option value="REGIONAL">Regional</option>
            <option value="OPTIONAL">Optional</option>
          </Select>
        </Field>
        {f.kind === "REGIONAL" && <Field label="Region" hint="Must match the region on the employee profile"><Input required value={f.region} onChange={set("region")} placeholder="e.g. Tamil Nadu" /></Field>}
        <div className="sm:col-span-2"><Field label="Description"><Input maxLength={255} value={f.description} onChange={set("description")} /></Field></div>
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

function Manage() {
  const toast = useToast();
  const [year, setYear] = useState(new Date().getFullYear());
  const { data, loading, reload } = useFetch("/holidays/", { year });
  const [form, setForm] = useState(null); // null = closed, {} = new, row = edit

  const remove = async (h) => {
    if (!confirm(`Delete "${h.name}"?`)) return;
    try { await api.delete(`/holidays/${h.id}/`); toast("Holiday deleted"); reload(); } catch (er) { toast(errMsg(er), "err"); }
  };

  return (
    <Card
      title="Holiday list"
      actions={
        <div className="flex items-center gap-2">
          <Input type="number" className="w-24" value={year} onChange={(e) => setYear(Number(e.target.value) || year)} />
          <Btn onClick={() => setForm({})}>Add holiday</Btn>
        </div>
      }
    >
      {loading ? <Spinner /> : (
        <Table
          rows={data || []}
          empty="No holidays defined for this year."
          columns={[
            { key: "date", label: "Date" },
            { label: "Day", render: (r) => new Date(r.date).toLocaleDateString("en-GB", { weekday: "short" }) },
            { key: "name", label: "Holiday" },
            { label: "Type", render: (r) => <Badge v={r.kind}>{r.kind_label}</Badge> },
            { label: "Region", render: (r) => r.region || "-" },
            { label: "Status", render: (r) => <Badge v={r.is_active ? "ACTIVE" : "INACTIVE"}>{r.is_active ? "Active" : "Inactive"}</Badge> },
            { label: "", render: (r) => (
              <div className="flex gap-2">
                <Btn small variant="secondary" onClick={() => setForm(r)}>Edit</Btn>
                <Btn small variant="danger" onClick={() => remove(r)}>Delete</Btn>
              </div>
            ) },
          ]}
        />
      )}
      {form && <HolidayForm initial={form.id ? form : null} onClose={() => setForm(null)} onSaved={reload} />}
    </Card>
  );
}

export default function Holidays() {
  const { isStaff } = useAuth();
  const [tab, setTab] = useState("calendar");
  const tabs = [{ key: "calendar", label: "Calendar" }, ...(isStaff ? [{ key: "manage", label: "Manage holidays" }] : [])];

  return (
    <>
      <PageHeader title="Holidays" sub="Company, regional and optional holidays. Company and regional holidays are excluded from attendance, leave and payroll." />
      {tabs.length > 1 && <Tabs tabs={tabs} value={tab} onChange={setTab} />}
      {tab === "calendar" ? <Card><HolidayCalendar /></Card> : <Manage />}
    </>
  );
}

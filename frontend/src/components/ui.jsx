import { createContext, useCallback, useContext, useEffect, useState } from "react";
import api, { errMsg } from "../api";

/* ---------- toast messages ---------- */
const ToastCtx = createContext(() => {});
export const useToast = () => useContext(ToastCtx);

export function ToastProvider({ children }) {
  const [items, setItems] = useState([]);

  const push = useCallback((msg, type = "ok") => {
    const id = Math.random();
    setItems((list) => [...list, { id, msg, type }]);
    setTimeout(() => setItems((list) => list.filter((x) => x.id !== id)), 4500);
  }, []);

  return (
    <ToastCtx.Provider value={push}>
      {children}
      <div className="fixed right-4 top-4 z-[100] max-w-sm space-y-2">
        {items.map((t) => (
          <div key={t.id} className={`rounded-xl px-4 py-3 text-sm text-white shadow-lg ${t.type === "err" ? "bg-rose-500" : "bg-emerald-500"}`}>
            {t.msg}
          </div>
        ))}
      </div>
    </ToastCtx.Provider>
  );
}

/* ---------- cards, buttons and form fields ---------- */
export const Card = ({ title, actions, children, className = "" }) => (
  <div className={`rounded-2xl bg-card shadow-[0_2px_14px_rgba(30,41,90,0.06)] ${className}`}>
    {(title || actions) && (
      <div className="flex items-center justify-between gap-3 px-6 pt-5">
        <h3 className="font-semibold text-slate-800">{title}</h3>
        <div className="flex gap-2">{actions}</div>
      </div>
    )}
    <div className={`px-6 pb-6 ${title || actions ? "pt-4" : "pt-6"}`}>{children}</div>
  </div>
);

const buttonColors = {
  primary: "bg-brand text-white hover:bg-brand-dark",
  secondary: "border border-slate-200 bg-card text-slate-600 hover:bg-slate-50",
  danger: "bg-rose-500 text-white hover:bg-rose-600",
  success: "bg-emerald-500 text-white hover:bg-emerald-600",
};

export const Btn = ({ variant = "primary", small, className = "", ...props }) => (
  <button
    {...props}
    className={`rounded-full font-medium transition disabled:cursor-not-allowed disabled:opacity-50 ${
      small ? "px-3 py-1 text-xs" : "px-5 py-2 text-sm"
    } ${buttonColors[variant]} ${className}`}
  />
);

export const Field = ({ label, children, hint }) => (
  <label className="block text-sm">
    <span className="mb-1 block text-xs font-medium text-slate-500">{label}</span>
    {children}
    {hint && <span className="mt-1 block text-xs text-slate-400">{hint}</span>}
  </label>
);

const inputBase =
  "border border-slate-200 bg-card px-4 py-2 text-sm focus:border-brand focus:outline-none focus:ring-2 focus:ring-brand/30";

// Inputs are full width by default. If a page passes its own width (like "w-40"),
// we skip "w-full", otherwise both classes fight each other and w-full wins.
const widthFor = (className) => (/(^|\s)w-/.test(className) ? "" : "w-full");

export const Input = ({ className = "", ...props }) => (
  <input {...props} className={`${inputBase} rounded-full ${widthFor(className)} ${className}`} />
);
export const Select = ({ children, className = "", ...props }) => (
  <select {...props} className={`${inputBase} rounded-full ${widthFor(className)} ${className}`}>{children}</select>
);
export const Textarea = ({ className = "", ...props }) => (
  <textarea rows={3} {...props} className={`${inputBase} rounded-2xl ${widthFor(className)} ${className}`} />
);

/* ---------- small display pieces ---------- */
const badgeColors = {
  PRESENT: "bg-emerald-100 text-emerald-700",
  APPROVED: "bg-emerald-100 text-emerald-700",
  CREDITED: "bg-emerald-100 text-emerald-700",
  SENT: "bg-emerald-100 text-emerald-700",
  PENDING: "bg-amber-100 text-amber-700",
  HALF_DAY: "bg-amber-100 text-amber-700",
  GENERATED: "bg-sky-100 text-sky-700",
  REJECTED: "bg-rose-100 text-rose-700",
  ABSENT: "bg-rose-100 text-rose-700",
  FAILED: "bg-rose-100 text-rose-700",
  CANCELLED: "bg-slate-200 text-slate-600",
  ADMIN: "bg-purple-100 text-purple-700",
  HR: "bg-indigo-100 text-indigo-700",
  EMPLOYEE: "bg-slate-100 text-slate-700",
};

export const Badge = ({ v, children }) => (
  <span className={`inline-block rounded-full px-2.5 py-0.5 text-xs font-medium ${badgeColors[v] || "bg-slate-100 text-slate-600"}`}>
    {children ?? String(v).replace("_", " ")}
  </span>
);

// Coloured summary box used at the top of dashboards
const statColors = {
  blue: { box: "bg-indigo-50", number: "text-indigo-500", bar: "bg-indigo-400" },
  green: { box: "bg-teal-50", number: "text-teal-500", bar: "bg-teal-400" },
  amber: { box: "bg-amber-50", number: "text-amber-500", bar: "bg-amber-400" },
  red: { box: "bg-rose-50", number: "text-rose-500", bar: "bg-rose-400" },
  slate: { box: "bg-slate-100", number: "text-slate-600", bar: "bg-slate-400" },
};

export const Stat = ({ label, value, sub, tone = "blue" }) => {
  const color = statColors[tone];
  return (
    <div className={`rounded-xl p-5 ${color.box}`}>
      <div className="flex items-center justify-between gap-3">
        <div>
          <div className="text-sm font-medium text-slate-700">{label}</div>
          <div className={`mt-2 h-1 w-8 rounded-full ${color.bar}`} />
        </div>
        <div className={`font-semibold ${color.number} ${String(value ?? "-").length > 7 ? "text-2xl" : "text-3xl"}`}>{value ?? "-"}</div>
      </div>
      {sub && <div className="mt-3 text-xs text-slate-500">{sub}</div>}
    </div>
  );
};

export const Spinner = () => <div className="p-8 text-center text-sm text-slate-400">Loading...</div>;
export const Empty = ({ children = "No records found." }) => <div className="p-8 text-center text-sm text-slate-400">{children}</div>;

export const PageHeader = ({ title, sub, children }) => (
  <div className="mb-6 flex flex-wrap items-center justify-between gap-3">
    <div>
      <h1 className="text-xl font-semibold text-slate-800">{title}</h1>
      {sub && <p className="text-sm text-slate-400">{sub}</p>}
    </div>
    <div className="flex flex-wrap gap-2">{children}</div>
  </div>
);

export function Modal({ title, onClose, children, wide }) {
  // close the popup when Esc is pressed
  useEffect(() => {
    const onKey = (e) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [onClose]);

  return (
    <div
      className="fixed inset-0 z-50 flex items-start justify-center overflow-y-auto bg-slate-900/40 p-4"
      onMouseDown={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className={`mt-10 w-full ${wide ? "max-w-3xl" : "max-w-lg"} rounded-2xl bg-card shadow-xl`}>
        <div className="flex items-center justify-between border-b border-slate-100 px-6 py-4">
          <h3 className="font-semibold text-slate-800">{title}</h3>
          <button onClick={onClose} className="text-2xl leading-none text-slate-400 hover:text-slate-700">&times;</button>
        </div>
        <div className="p-6">{children}</div>
      </div>
    </div>
  );
}

export function Tabs({ tabs, value, onChange }) {
  return (
    <div className="mb-5 flex gap-1 border-b border-slate-200">
      {tabs.map((tab) => (
        <button
          key={tab.key}
          onClick={() => onChange(tab.key)}
          className={`-mb-px border-b-2 px-4 py-2 text-sm font-medium ${
            value === tab.key ? "border-brand text-brand" : "border-transparent text-slate-500 hover:text-slate-700"
          }`}
        >
          {tab.label}
        </button>
      ))}
    </div>
  );
}

/* columns: [{ key | render, label, className }] */
export function Table({ columns, rows, empty }) {
  if (!rows?.length) return <Empty>{empty}</Empty>;
  return (
    <div className="overflow-x-auto">
      <table className="min-w-full text-sm">
        <thead>
          <tr className="border-b border-slate-200 text-left text-xs font-semibold text-slate-500">
            {columns.map((col, i) => (
              <th key={i} className={`px-3 py-3 ${col.className || ""}`}>{col.label}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, rowIndex) => (
            <tr key={row.id ?? rowIndex} className="border-b border-slate-100 last:border-0 hover:bg-slate-50">
              {columns.map((col, i) => (
                <td key={i} className={`px-3 py-3 ${col.className || ""}`}>
                  {col.render ? col.render(row) : row[col.key] ?? "-"}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

export function Pager({ page, setPage, count, size = 20 }) {
  const pages = Math.max(1, Math.ceil(count / size));
  if (pages <= 1) return null;
  return (
    <div className="mt-4 flex items-center justify-end gap-3 text-sm text-slate-500">
      <span>Page {page} of {pages} ({count} records)</span>
      <Btn variant="secondary" small disabled={page <= 1} onClick={() => setPage(page - 1)}>Prev</Btn>
      <Btn variant="secondary" small disabled={page >= pages} onClick={() => setPage(page + 1)}>Next</Btn>
    </div>
  );
}

/* ---------- data hooks ---------- */
export function usePaged(url, params = {}, enabled = true) {
  const toast = useToast();
  const [page, setPage] = useState(1);
  const [state, setState] = useState({ rows: [], count: 0, loading: true });
  const key = JSON.stringify(params);
  const load = useCallback(() => {
    if (!enabled) return;
    setState((s) => ({ ...s, loading: true }));
    const clean = Object.fromEntries(Object.entries(JSON.parse(key)).filter(([, v]) => v !== "" && v != null));
    api.get(url, { params: { ...clean, page } })
      .then((r) => setState({ rows: r.data.results ?? r.data, count: r.data.count ?? r.data.length, loading: false }))
      .catch((e) => { toast(errMsg(e), "err"); setState({ rows: [], count: 0, loading: false }); });
  }, [url, key, page, enabled]); // eslint-disable-line
  useEffect(() => { setPage(1); }, [key]);
  useEffect(load, [load]);
  return { ...state, page, setPage, reload: load };
}

export function useFetch(url, params, enabled = true) {
  const toast = useToast();
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const key = JSON.stringify(params || {});
  const load = useCallback(() => {
    if (!enabled) return;
    setLoading(true);
    api.get(url, { params: JSON.parse(key) }).then((r) => setData(r.data)).catch((e) => toast(errMsg(e), "err")).finally(() => setLoading(false));
  }, [url, key, enabled]); // eslint-disable-line
  useEffect(load, [load]);
  return { data, loading, reload: load };
}

export const fmtMoney = (v) => (v == null ? "-" : Number(v).toLocaleString("en-IN", { minimumFractionDigits: 2, maximumFractionDigits: 2 }));
export const fmtTime = (iso) => (iso ? new Date(iso).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : "-");
export const fmtDateTime = (iso) => (iso ? new Date(iso).toLocaleString() : "-");
export const MONTHS = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
export const lastMonth = () => { const d = new Date(); d.setDate(1); d.setMonth(d.getMonth() - 1); return { year: d.getFullYear(), month: d.getMonth() + 1 }; };

import { useState } from "react";
import { Badge, useFetch } from "./ui";

const CHART_COLORS = ["#4f46e5", "#10b981", "#f59e0b", "#ec4899", "#0ea5e9", "#8b5cf6"];

// Donut chart drawn with SVG circles. data = [{ label, value }]
export function DonutChart({ data, centerValue, centerLabel }) {
  const total = data.reduce((sum, item) => sum + item.value, 0);
  const radius = 52;
  const circumference = 2 * Math.PI * radius;
  let used = 0; // how much of the circle is already painted

  return (
    <div className="flex flex-col items-center gap-5 sm:flex-row sm:justify-around">
      <div className="relative h-40 w-40 shrink-0">
        <svg viewBox="0 0 140 140" className="h-full w-full -rotate-90">
          <circle cx="70" cy="70" r={radius} fill="none" stroke="#f1f5f9" strokeWidth="16" />
          {total > 0 &&
            data.map((item, index) => {
              const length = (item.value / total) * circumference;
              const slice = (
                <circle
                  key={item.label}
                  cx="70"
                  cy="70"
                  r={radius}
                  fill="none"
                  stroke={CHART_COLORS[index % CHART_COLORS.length]}
                  strokeWidth="16"
                  strokeDasharray={`${length} ${circumference - length}`}
                  strokeDashoffset={-used}
                />
              );
              used += length;
              return slice;
            })}
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className="text-3xl font-semibold text-slate-800">{centerValue}</span>
          <span className="text-xs text-slate-400">{centerLabel}</span>
        </div>
      </div>

      <ul className="space-y-2 text-sm">
        {data.map((item, index) => (
          <li key={item.label} className="flex items-center gap-2">
            <span className="h-2.5 w-2.5 rounded-full" style={{ background: CHART_COLORS[index % CHART_COLORS.length] }} />
            <span className="text-slate-600">{item.label}</span>
            <span className="ml-auto pl-4 font-medium text-slate-800">{item.value}</span>
          </li>
        ))}
      </ul>
    </div>
  );
}

const WEEK_DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

// Month calendar with today highlighted
export function MiniCalendar() {
  const today = new Date();
  const [shown, setShown] = useState(new Date(today.getFullYear(), today.getMonth(), 1));

  const year = shown.getFullYear();
  const month = shown.getMonth();
  const monthName = shown.toLocaleString("en-US", { month: "long" });

  const emptyCells = (new Date(year, month, 1).getDay() + 6) % 7; // our week starts on Monday
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [...Array(emptyCells).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)];

  const isToday = (day) => day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
  const changeMonth = (step) => setShown(new Date(year, month + step, 1));

  return (
    <div>
      <div className="mb-3 flex items-center justify-between">
        <button onClick={() => changeMonth(-1)} className="px-2 text-lg text-slate-400 hover:text-brand">&lsaquo;</button>
        <span className="text-sm font-medium text-slate-700">{monthName} {year}</span>
        <button onClick={() => changeMonth(1)} className="px-2 text-lg text-slate-400 hover:text-brand">&rsaquo;</button>
      </div>
      <div className="grid grid-cols-7 gap-y-1 text-center text-xs">
        {WEEK_DAYS.map((d) => (
          <div key={d} className="pb-1 text-slate-400">{d}</div>
        ))}
        {cells.map((day, i) => (
          <div key={i} className="flex justify-center">
            {day && (
              <span className={`flex h-7 w-7 items-center justify-center rounded-full ${isToday(day) ? "bg-brand font-medium text-white" : "text-slate-600"}`}>
                {day}
              </span>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}


/* ---------- Holiday calendar (monthly + yearly view) ---------- */
const HOLIDAY_STYLE = {
  COMPANY: { cell: "bg-rose-100 text-rose-700", dot: "bg-rose-400", label: "Company holiday" },
  REGIONAL: { cell: "bg-amber-100 text-amber-700", dot: "bg-amber-400", label: "Regional holiday" },
  OPTIONAL: { cell: "bg-sky-100 text-sky-700", dot: "bg-sky-400", label: "Optional holiday" },
};
const KIND_ORDER = ["COMPANY", "REGIONAL", "OPTIONAL"]; // which colour wins when two holidays share a day

const dateKey = (year, month, day) => `${year}-${String(month + 1).padStart(2, "0")}-${String(day).padStart(2, "0")}`;

// One month as a grid. `small` is used in the yearly view.
function MonthGrid({ year, month, byDate, small, onTitleClick }) {
  const today = new Date();
  const emptyCells = (new Date(year, month, 1).getDay() + 6) % 7; // week starts on Monday
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const cells = [...Array(emptyCells).fill(null), ...Array.from({ length: daysInMonth }, (_, i) => i + 1)];
  const isToday = (day) => day === today.getDate() && month === today.getMonth() && year === today.getFullYear();
  const size = small ? "h-6 w-6 text-[10px]" : "h-8 w-8 text-xs";

  return (
    <div>
      {small && (
        <button onClick={onTitleClick} className="mb-1 w-full text-left text-sm font-medium text-slate-700 hover:text-brand">
          {new Date(year, month, 1).toLocaleString("en-US", { month: "long" })}
        </button>
      )}
      <div className="grid grid-cols-7 gap-y-1 text-center">
        {WEEK_DAYS.map((d) => (
          <div key={d} className={`pb-1 text-slate-400 ${small ? "text-[9px]" : "text-xs"}`}>{small ? d[0] : d}</div>
        ))}
        {cells.map((day, i) => {
          const list = day ? byDate[dateKey(year, month, day)] : null;
          const kind = list && KIND_ORDER.find((k) => list.some((h) => h.kind === k));
          const weekend = i % 7 >= 5;
          const style = kind ? HOLIDAY_STYLE[kind].cell : isToday(day) ? "bg-brand font-medium text-white" : weekend ? "text-slate-400" : "text-slate-600";
          return (
            <div key={i} className="flex justify-center">
              {day && (
                <span
                  title={list ? list.map((h) => h.name).join(", ") : undefined}
                  className={`flex items-center justify-center rounded-full ${size} ${style} ${kind && isToday(day) ? "ring-2 ring-brand" : ""}`}
                >
                  {day}
                </span>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}

export function HolidayCalendar() {
  const now = new Date();
  const [view, setView] = useState("month"); // "month" | "year"
  const [shown, setShown] = useState({ year: now.getFullYear(), month: now.getMonth() });
  const { data } = useFetch("/holidays/", { year: shown.year });

  const byDate = {};
  (data || []).forEach((h) => { byDate[h.date] = [...(byDate[h.date] || []), h]; });

  const step = (n) => {
    if (view === "year") return setShown({ ...shown, year: shown.year + n });
    const d = new Date(shown.year, shown.month + n, 1);
    setShown({ year: d.getFullYear(), month: d.getMonth() });
  };
  const monthName = new Date(shown.year, shown.month, 1).toLocaleString("en-US", { month: "long" });
  const thisMonth = (data || []).filter((h) => new Date(h.date).getMonth() === shown.month);

  return (
    <div>
      <div className="mb-3 flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-1">
          <button onClick={() => step(-1)} className="px-2 text-lg text-slate-400 hover:text-brand">&lsaquo;</button>
          <span className="min-w-32 text-center text-sm font-medium text-slate-700">{view === "year" ? shown.year : `${monthName} ${shown.year}`}</span>
          <button onClick={() => step(1)} className="px-2 text-lg text-slate-400 hover:text-brand">&rsaquo;</button>
        </div>
        <div className="flex gap-1">
          {["month", "year"].map((v) => (
            <button key={v} onClick={() => setView(v)} className={`rounded-full px-3 py-1 text-xs font-medium ${view === v ? "bg-brand text-white" : "border border-slate-200 text-slate-600 hover:bg-slate-50"}`}>
              {v === "month" ? "Month" : "Year"}
            </button>
          ))}
        </div>
      </div>

      {view === "month" ? (
        <>
          <MonthGrid year={shown.year} month={shown.month} byDate={byDate} />
          <ul className="mt-4 space-y-2 text-sm">
            {thisMonth.length === 0 && <li className="text-xs text-slate-400">No holidays this month.</li>}
            {thisMonth.map((h) => (
              <li key={h.id} className="flex items-center gap-2">
                <span className={`h-2.5 w-2.5 shrink-0 rounded-full ${HOLIDAY_STYLE[h.kind].dot}`} />
                <span className="text-slate-500">{new Date(h.date).toLocaleDateString("en-GB", { day: "2-digit", month: "short", weekday: "short" })}</span>
                <span className="font-medium text-slate-700">{h.name}</span>
                {h.region && <span className="text-xs text-slate-400">({h.region})</span>}
                <span className="ml-auto"><Badge v={h.kind} /></span>
              </li>
            ))}
          </ul>
        </>
      ) : (
        <div className="grid grid-cols-2 gap-5 sm:grid-cols-3 xl:grid-cols-4">
          {Array.from({ length: 12 }, (_, m) => (
            <MonthGrid key={m} year={shown.year} month={m} byDate={byDate} small onTitleClick={() => { setShown({ ...shown, month: m }); setView("month"); }} />
          ))}
        </div>
      )}

      <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
        {KIND_ORDER.map((k) => (
          <span key={k} className="flex items-center gap-1.5"><span className={`h-2.5 w-2.5 rounded-full ${HOLIDAY_STYLE[k].dot}`} />{HOLIDAY_STYLE[k].label}</span>
        ))}
      </div>
    </div>
  );
}

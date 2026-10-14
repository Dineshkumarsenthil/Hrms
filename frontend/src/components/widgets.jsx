import { useState } from "react";

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

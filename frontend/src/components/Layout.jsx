import { useEffect, useState } from "react";
import { Link, NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import Icon from "./Icons";
import NotificationBell from "./NotificationBell";
import ThemeToggle from "./ThemeToggle";

const ROLE_LABEL = { ADMIN: "Admin", HR: "HR", EMPLOYEE: "Employee" };

// Date and time shown in the top bar, refreshed every 30 seconds
function useClock() {
  const [now, setNow] = useState(new Date());
  useEffect(() => {
    const timer = setInterval(() => setNow(new Date()), 30000);
    return () => clearInterval(timer);
  }, []);
  return {
    date: now.toLocaleDateString("en-GB").replaceAll("/", "."),
    time: now.toLocaleTimeString("en-US", { hour: "2-digit", minute: "2-digit" }).toLowerCase(),
  };
}

export default function Layout() {
  const { user, logout, isStaff, isAdmin } = useAuth();
  const navigate = useNavigate();
  const { date, time } = useClock();
  const [quickOpen, setQuickOpen] = useState(false);

  // [path, label, icon]
  const links = [
    ["/", "Dashboard", "home"],
    ...(user.has_employee ? [["/profile", "My Profile", "user"]] : []),
    ...(isStaff ? [["/employees", "Employees", "users"]] : []),
    ["/attendance", "Attendance", "clock"],
    ["/leaves", "Leave", "calendar"],
    ["/holidays", "Holidays", "flag"],
    ["/shifts", "Shifts", "swap"],
    ["/payroll", isStaff ? "Payroll" : "Salary Slips", "wallet"],
    ["/notifications", "Notifications", "bell"],
    ...(isStaff ? [["/reports", "Reports", "chart"], ["/audit", "Audit Logs", "shield"], ["/emails", "Email Logs", "mail"]] : []),
    ...(isAdmin ? [["/users", "Users & Roles", "lock"]] : []),
  ];

  const fullName = `${user.first_name || user.username} ${user.last_name || ""}`.trim();
  const initials = (user.first_name?.[0] || user.username[0]).toUpperCase() + (user.last_name?.[0] || "").toUpperCase();

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  return (
    <div className="min-h-screen bg-page p-4">
      {/* top bar */}
      <header className="mb-4 flex items-center justify-between rounded-2xl bg-card px-6 py-3 shadow-[0_2px_14px_rgba(30,41,90,0.06)]">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand text-lg font-semibold text-white">H</div>
          <div>
            <div className="text-sm font-semibold leading-tight text-slate-800">HRMS</div>
            <div className="text-xs text-slate-400">Human Resource Management System</div>
          </div>
        </div>

        <div className="flex items-center gap-5 text-sm text-slate-600">
          <span className="hidden sm:inline">{date}</span>
          <span className="hidden h-4 w-px bg-slate-200 sm:inline-block" />
          <span className="hidden sm:inline">{time}</span>

          <div className="relative" onMouseLeave={() => setQuickOpen(false)}>
            <button onClick={() => setQuickOpen(!quickOpen)} className="flex items-center gap-2">
              <span className="hidden sm:inline">Quick links</span>
              <span className="flex h-8 w-8 items-center justify-center rounded-full bg-slate-100 text-slate-500">
                <Icon name="grid" className="h-4 w-4" />
              </span>
            </button>
            {quickOpen && (
              <div className="absolute right-0 top-10 z-40 w-48 rounded-xl bg-card p-2 shadow-lg ring-1 ring-slate-100">
                {links.map(([path, label]) => (
                  <Link key={path} to={path} onClick={() => setQuickOpen(false)} className="block rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-brand-soft hover:text-brand">
                    {label}
                  </Link>
                ))}
              </div>
            )}
          </div>

          <ThemeToggle />

          <NotificationBell />
          <button onClick={handleLogout} title="Log out" className="text-slate-500 hover:text-brand">
            <Icon name="logout" />
          </button>
        </div>
      </header>

      <div className="flex flex-col gap-4 lg:flex-row">
        {/* sidebar */}
        <aside className="w-full shrink-0 rounded-2xl bg-card py-5 shadow-[0_2px_14px_rgba(30,41,90,0.06)] lg:w-64">
          <div className="flex items-center gap-3 px-5">
            <div className="flex h-12 w-12 items-center justify-center rounded-full bg-brand-soft text-sm font-semibold text-brand">{initials}</div>
            <div className="min-w-0">
              <div className="text-xs text-slate-400">Welcome,</div>
              <div className="truncate text-sm font-semibold text-slate-800">{fullName}</div>
            </div>
          </div>

          <div className="mx-5 mt-5 border-b border-slate-100">
            <span className="inline-block border-b-2 border-brand pb-1 text-sm font-semibold text-brand">{ROLE_LABEL[user.role]}</span>
          </div>

          <nav className="mt-3 space-y-1 px-3">
            {links.map(([path, label, icon]) => (
              <NavLink
                key={path}
                to={path}
                end={path === "/"}
                className={({ isActive }) =>
                  `flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm ${
                    isActive ? "bg-brand-soft font-medium text-brand" : "text-slate-600 hover:bg-slate-50"
                  }`
                }
              >
                <Icon name={icon} className="h-[18px] w-[18px]" />
                {label}
              </NavLink>
            ))}
          </nav>
        </aside>

        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
